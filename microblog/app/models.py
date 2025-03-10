from app import db, login
from app.search import add_to_index, query_index, remove_from_index
from datetime import datetime
from flask import current_app
from flask_login import UserMixin
from hashlib import md5
from time import time
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import json
import redis
import rq


# Table au lieu de Model si many-to-many et pas d'attribut supplémentaire
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

# Chaque modèle a une attribut 'query' pour faire des requêtes...

# 'backref' détermine le champ qu'il sera ajouté dans l'objet visé
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
                    'User', 
                    secondary = followers,
                    primaryjoin = (followers.c.follower_id == id),
                    secondaryjoin = (followers.c.followed_id == id),
                    backref = db.backref('followers', lazy = 'dynamic'), 
                    lazy = 'dynamic'
               )
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author',
                                    lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient',
                                        lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)
    notifications = db.relationship('Notification', backref='user',
                                    lazy='dynamic')
    tasks = db.relationship('Task', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'\
               .format(digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id = self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    # Nombre de messages non lu
    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        notifications = Notification(name=name, payload_json=json.dumps(data),
                                      user=self)
        db.session.add(notifications)
        return notifications
    
    def launch_task(self, name, description, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue('app.tasks.' + name, self.id,
                                                *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name, description=description,
                    user=self)
        db.session.add(task)
        return task
    
    def get_tasks_in_progress(self):
        return Task.query.filter_by(user=self, complete=False).all()
    
    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, user=self,
                                    complte=False).first()
        

class SearchableMixin(object):
    # classmethod : traite une fonction comme une classe et premier argument
    # étant la classe dans lequel il est appelé
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        # Sous forme de tuple, on index les trouvailles car elasticSearch
        # tri les ids du plus important au moins important donc nous faisons
        # la même chose
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        # SELECT id FROM Post WHERE id IN (ids)
        # Argument optionnel 'value': pour signifier que tout 'id' qu'il 
        # proviennent de 'post.id'
        # Ex de when: [(22, 0), (23, 1)]
        #             case post.id
        #             when '22' then 0
        #             when '23' then 1
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total
    
    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),       # pending object
            'update': list(session.dirty),  # changes detect
            'delete': list(session.deleted) # mark as delete
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


class Post(SearchableMixin, db.Model):
    __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))


class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    complete = db.Column(db.Boolean, default=False)
    
    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job
    
    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100
            

class BusinessMontreal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    address = db.Column(db.String(128), index=True)
    city = db.Column(db.String(128), index=True)
    state = db.Column(db.String(128), index=True)
    type = db.Column(db.String(128), index=True)
    statut = db.Column(db.String(128), index=True)
    date_statut = db.Column(db.DateTime, index=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    date_last_update = db.Column(db.DateTime, index=True)

    def as_dict(self):
        return {'business_id': self.id,
                'name': self.name,
                'address': self.address,
                'city': self.city,
                'state': self.state,
                'type': self.type,
                'statut': self.statut,
                'date_statut': self.date_statut,
                'latitude': self.latitude,
                'longitude': self.longitude,
                'x': self.x,
                'y': self.y,
                'date_last_update': self.date_last_update}

    def to_dict(self):
        return {'business_id': str(self.id),
                'name': str(self.name),
                'address': str(self.address),
                'city': str(self.city),
                'state': str(self.state),
                'type': str(self.type),
                'statut': str(self.statut),
                'date_statut': self.date_statut.strftime("%Y%m%d"),
                'latitude': str(self.latitude),
                'longitude': str(self.longitude),
                'x': str(self.x),
                'y': str(self.y),
                'date_last_update': self.date_last_update.strftime("%Y%m%d")}


    def update_from_dict(self, dict):
        self.id = dict.get('business_id', self.id)
        self.name = dict.get('name', self.name)
        self.address = dict.get('address', self.address)
        self.city = dict.get('city', self.city)
        self.state = dict.get('state', self.state)
        self.type = dict.get('type', self.type)
        self.statut = dict.get('statut', self.statut)
        self.date_statut = datetime.strptime(dict.get('date_statut', 
                                                      self.date_statut),
                                             '%Y%m%d').date()
        self.latitude = string_to_float(dict.get('latitude', self.latitude))
        self.longitude = string_to_float(dict.get('longitude', self.longitude))
        self.x = string_to_float(dict.get('x', self.x))
        self.y = string_to_float(dict.get('y', self.y))
        self.date_last_update = datetime.strptime(dict.get('date_last_update', 
                                                    self.date_last_update),
                                                    '%Y%m%d').date()


    def __repr__(self):
        return '{}'.format(self.name)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

# Gère un float '' pour retourner None...
def string_to_float(string):
    try:
        return float(string)
    except ValueError:
        return None

@login.user_loader
def load_user(id):
    return User.query.get(int(id))