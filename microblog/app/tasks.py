import csv
import json
import tweepy
import time
import pandas as pd
import polars as pl
from app import db
from app.models import BusinessMontreal, User, Post, Message, Notification, \
                       Task
from datetime import datetime
from rq import get_current_job
from urllib.request import urlopen

"""
def example(seconds):
    job = get_current_job()
    print('Starting task')
    for i in range(seconds):
        job.meta['progress'] = 100.0 * i / seconds
        job.save_meta()
        print(i)
        time.sleep(1)
    job.meta['progress'] = 100
    job.save_meta()
    print('Task completed')
"""

def example2():
    print('TEST')


# TODO: à effacer à la fin les print!
# Possible que ça puisse prendre du temps à charger, trouver solution
def import_data_business_montreal():
    print('BONJOUR!')
    try:
        """
        import_data_to_csv("https://donnees.montreal.ca/dataset/c1d65779-d3cb"
                           "-44e8-af0a-b9f2c5f7766d/resource/28a4957d-732e"
                           "-48f9-8adb-0624867d9bb0/download/businesses.csv",
                           "business_montreal") 
        """
        result = import_csv_to_database("business_montreal")
        # Exporte les données avant sa MAJ
        export_csv_data_to_csv(
            "business_montreal",
            result[3], 
            "before_update_data_business_montreal"
        )
        # Exporte les données après sa MAJ
        export_csv_data_to_csv(
            "business_montreal",
            result[2], 
            "update_data_business_montreal"
        )
        convert_csv_to_json("business_montreal")
        print('FINI :)')
        return result
    except Exception as e:
        print(e)


def import_data_to_csv(link, write_file_name):
    url = urlopen("{}".format(link))
    string = url.read().decode('utf-8')
    try:
        file = open("app/static/data/{}.csv".format(write_file_name), "w")
    except Exception as e:
        print(e)
    file.write(string)
    file.close()
    

def import_csv_to_database(read_file_name):
    #with db.session.begin():
    #    db.session.query(BusinessMontreal).delete()
    with open("app/static/data/{}.csv".format(read_file_name), 'r') as file:
        reader = csv.DictReader(file)
        #next(reader)
        new_record_list = []
        before_record_update_list = []
        existing_record_update_list = []
        current_ids = set()
        # Importe l'heure actuelle
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
        current_datetime = datetime.strptime(formatted_datetime, 
                                             "%Y-%m-%d %H:%M:%S")
        existing_records = db.session.query(BusinessMontreal).all()
        # Sauvegarde les ids pour comparaison entre csv et la bd
        df = pl.read_csv(("app/static/data/{}.csv".format(read_file_name)))
        current_ids = set(df['business_id'].to_list())
        #for record in existing_records:
        #    print(record.id)
        #    current_ids.add(record.id)
        for row in reader:
            date = datetime.strptime(row['date_statut'], '%Y%m%d').date()
            with db.session.no_autoflush:
                existing_record = db.session.query(BusinessMontreal).\
                                        filter_by(id=row['business_id']).\
                                        first()
                                        
                new_record = BusinessMontreal(
                    id=row['business_id'], name=row['name'],
                    address=row['address'], city=row['city'],
                    state=row['state'], type=row['type'],
                    statut=row['statut'], date_statut=date,
                    latitude=string_to_float(row['latitude']),
                    longitude=string_to_float(row['longitude']),
                    x=string_to_float(row['x']),
                    y=string_to_float(row['y']),
                    date_last_update=current_datetime)

                # S'il y a une mise à jour à faire
                if existing_record is not None and \
                    existing_record.to_dict() != new_record.to_dict():
                    before_record_update_list.append(existing_record.as_dict())
                    existing_record.update_from_dict(row)
                    db.session.commit()
                    existing_record_update_list.append(
                        existing_record.as_dict())
                elif existing_record is None:
                    db.session.add(new_record)
                    new_record_list.append(new_record)

    
        # Identifier les IDs à supprimer
        ids_to_delete = [record.id for record in existing_records if record.id not in current_ids]
        print(ids_to_delete)
        # Supprimer les enregistrements correspondants de la base de données
        for id_to_delete in ids_to_delete:
            print(id_to_delete)
            record_to_delete = db.session.query(BusinessMontreal).filter_by(id=id_to_delete).first()
            db.session.delete(record_to_delete)
        
        print('New record:')       
        print(new_record_list)
        print('Before record:')
        print(before_record_update_list)
        print('update record:')
        print(existing_record_update_list)
        db.session.commit() 
        return 'Data imported successfully', new_record_list, \
                existing_record_update_list, before_record_update_list

def compare_rows_csv_to_db(read_file_name):
    df_csv = pd.read_csv("app/static/data/{}.csv".format(read_file_name), 'r')


def export_csv_data_to_csv(source_csv, data, destination_csv):
    try:
        # Obtenir le nom des colonnes appropriées
        fieldnames = obtain_column_name_csv(source_csv)
        # Écriture des données
        with open("app/static/data/{}.csv".format(destination_csv), \
            'w') as destination_csv:
            writer = csv.DictWriter(destination_csv, fieldnames=fieldnames)
            writer.writeheader()
            # Écriture des données
            for row in data:
                writer.writerow(row)
    except Exception as e:
        print(e)


def add_todays_date_column_csv(file_name):
    try:
        # Obtenir le nom des colonnes appropriées
        existing_fieldnames = obtain_column_name_csv(file_name)
        new_fieldnames = "date_update"
        # Écriture des mises à jour des données
        with open("app/static/data/{}.csv".format(file_name), \
            'w') as destination_csv:
            # Importe l'heure actuelle
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
            writer = csv.DictWriter(destination_csv, fieldnames=
                                    existing_fieldnames + [new_fieldnames])
            # Écriture des données
            for row in file_name:
                writer.writerow({})
    except Exception as e:
        print(e)


def obtain_column_name_csv(file_name):
    try:
        # Obtenir le nom des colonnes appropriées
        with open("app/static/data/{}.csv".format(file_name), \
            'r') as source_csv:
            reader = csv.reader(source_csv)
            fieldnames = next(reader)
        return fieldnames
    except Exception as e:
        print(e)


def read_csv(file_name):
    try:
        with open("app/static/data/{}.csv".format(file_name), "r") as file:
            reader = csv.DictReader(file)
            data = []
            for row in reader:
                data.append(row)
                
            return data
    except Exception as e:
        print(e)
    file.close()


def create_tweet():
    
    
    return None


# Gère un float '' pour retourner None...
def string_to_float(string):
    try:
        return float(string)
    except ValueError:
        return None
    
    
def convert_csv_to_json(file_name):
    # Open the CSV file and read its contents into a list of dictionaries
    with open('app/static/data/{}.csv'.format(file_name), 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]

    # Write the list of dictionaries to a JSON file
    with open('app/static/data/{}.json'.format(file_name), 'w') as jsonfile:
        json.dump(data, jsonfile)
    
    
def clear_users_related_tables():
    clear_message_table()
    clear_notification_table()
    clear_post_table()
    clear_user_table()


def clear_message_table():
    db.session.query(Message).delete()
    db.session.commit()
    
    
def clear_notification_table():
    db.session.query(Notification).delete()
    db.session.commit()

    
def clear_post_table():
    db.session.query(Post).delete()
    db.session.commit()
    

def clear_user_table():
    db.session.query(User).delete()
    db.session.commit()

    
def clear_task_table():
    db.session.query(Task).delete()
    db.session.commit()