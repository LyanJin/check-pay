from app.enums.trade import PayTypeEnum
from app.extensions import scheduler

from app.models.order.order import OrderDeposit, OrderWithdraw
from app.models.order.order_detail import OrderDetailDeposit, OrderDetailWithdraw


# @scheduler.task('interval', id='batch_add_test_orders', seconds=60)
def batch_add_test_orders():
    # @scheduler.task('interval', id='batch_add_test_orders', minutes=30)
    # 定时添加一些测试数据
    from app.main import flask_app
    from scripts.order_mix import OrderMixes

    print('job batch_add_test_orders running')

    day_num = 5
    uid_range = range(1000, 1021)

    with flask_app.app_context():
        OrderMixes(PayTypeEnum.DEPOSIT).batch_add_orders_no_check(day_num, uid_range)
        OrderMixes(PayTypeEnum.WITHDRAW).batch_add_orders_no_check(day_num, uid_range)


# @scheduler.task('interval', id='clean_order_table', minutes=10)
@scheduler.task('cron', id="clean_order_table", hour=4)
def clean_order_table():
    # 每天凌晨4点清理数据
    from app.main import flask_app

    print('job clean_order_table running')

    with flask_app.app_context():
        rst = OrderDeposit.clean_hot_table()
        print(rst)
        rst = OrderWithdraw.clean_hot_table()
        print(rst)
        rst = OrderDetailDeposit.clean_hot_table()
        print(rst)
        rst = OrderDetailWithdraw.clean_hot_table()
        print(rst)
