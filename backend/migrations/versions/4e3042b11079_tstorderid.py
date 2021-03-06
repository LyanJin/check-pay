"""tstorderid

Revision ID: 4e3042b11079
Revises: 003e9d65cbdc
Create Date: 2019-09-05 15:30:15.329812

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e3042b11079'
down_revision = '003e9d65cbdc'
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()





def upgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order_tst_gid',
    sa.Column('create_time', sa.Integer(), nullable=False, comment='创建时间'),
    sa.Column('update_time', sa.Integer(), nullable=False, comment='更新时间'),
    sa.Column('uid', sa.Integer(), nullable=False, comment='用户ID'),
    sa.Column('sys_tx_id', sa.String(length=128), nullable=False, comment='系统交易ID'),
    sa.Column('mch_tx_id', sa.String(length=128), nullable=False, comment='商户交易ID'),
    sa.Column('channel_tx_id', sa.String(length=128), nullable=True, comment='通道交易ID'),
    sa.Column('amount', sa.BigInteger(), nullable=False, comment='订单发起金额'),
    sa.Column('tx_amount', sa.BigInteger(), nullable=True, comment='实际支付金额'),
    sa.Column('source', sa.SmallInteger(), nullable=False, comment='订单来源'),
    sa.Column('p_method', sa.SmallInteger(), nullable=True, comment='支付方法'),
    sa.Column('state', sa.SmallInteger(), nullable=False, comment='订单状态'),
    sa.Column('settle', sa.SmallInteger(), nullable=False, comment='结算状态'),
    sa.Column('deliver', sa.SmallInteger(), nullable=False, comment='发货(通知)状态'),
    sa.Column('channel_id', sa.Integer(), nullable=True, comment='渠道费率配置ID'),
    sa.Column('mch_fee_id', sa.Integer(), nullable=True, comment='商户费率配置ID'),
    sa.Column('notify_url', sa.String(length=256), nullable=True, comment='通知URL'),
    sa.Column('extra', sa.Text(), nullable=True, comment='透传数据'),
    sa.Column('merchant', sa.Integer(), nullable=False, comment='商户ID'),
    sa.Column('id', sa.BigInteger(), autoincrement=False, nullable=False, comment='订单ID'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('mch_tx_id'),
    sa.UniqueConstraint('sys_tx_id')
    )
    # ### end Alembic commands ###


def downgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('order_tst_gid')
    # ### end Alembic commands ###


def upgrade_BACK():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade_BACK():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

