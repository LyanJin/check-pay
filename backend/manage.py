from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

import config
from app.main import flask_app
from app.extensions import db

manager = Manager(flask_app)

migrate = Migrate(flask_app, db)
manager.add_command('db', MigrateCommand)


@manager.shell
def make_shell_context():
    return dict(app=flask_app, db=db, config=config)


@manager.command
def init_db():
    from app.models.bank import Bank
    Bank.init_bank_data()


@manager.option('--account', '-a', dest='account', required=True, help="admin account")
@manager.option('--password', '-p', dest='password', default=None, help="admin password")
def init_admin(account, password):
    from scripts.admin_user import init_admin_user
    init_admin_user(account, password)


@manager.option('--account', '-a', dest='account', required=True, help="user account")
@manager.option('--balance', '-b', dest='balance', required=True, help="balance to plus or minus")
def alter_user_balance(account, balance):
    from scripts.user_balance import add_user_balance
    add_user_balance(account, balance)


if __name__ == '__main__':
    manager.run()
