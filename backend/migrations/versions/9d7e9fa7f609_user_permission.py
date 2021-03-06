"""user_permission

Revision ID: 9d7e9fa7f609
Revises: 64a73a1e5d68
Create Date: 2019-09-18 12:40:46.517530

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d7e9fa7f609'
down_revision = '64a73a1e5d68'
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()





def upgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('permissions', sa.SmallInteger(), nullable=True, comment='账号权限'))
    # ### end Alembic commands ###


def downgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'permissions')
    # ### end Alembic commands ###


def upgrade_BACK():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade_BACK():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

