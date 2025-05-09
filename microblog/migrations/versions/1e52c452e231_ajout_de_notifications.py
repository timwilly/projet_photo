"""Ajout de notifications

Revision ID: 1e52c452e231
Revises: 0a9ae4b0eaae
Create Date: 2023-01-28 20:31:58.354432

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e52c452e231'
down_revision = '0a9ae4b0eaae'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.Float(), nullable=True),
    sa.Column('payload_json', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_name'), 'notifications', ['name'], unique=False)
    op.create_index(op.f('ix_notifications_timestamp'), 'notifications', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_notifications_timestamp'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_name'), table_name='notifications')
    op.drop_table('notifications')
    # ### end Alembic commands ###
