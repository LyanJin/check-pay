"""SQLAlchemy扩展
"""
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, BaseQuery
from contextlib import contextmanager

from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles


@compiles(BigInteger, 'sqlite')
def bi_c(element, compiler, **kw):
    """
    解决sqlite不支持BigInteger AUTOINCREMENT 主键问题
    :param element:
    :param compiler:
    :param kw:
    :return:
    """
    return "INTEGER"


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self, commit=True):
        """
        自动提交事务
        :param commit: 是否立即提交
        :return:
        """
        try:
            yield
            commit and self.session.commit()
        except Exception as e:
            commit and self.session.rollback()
            raise e


class Query(BaseQuery):
    def filter_by(self, **kwargs):
        return super(Query, self).filter_by(**kwargs)


db = SQLAlchemy(query_class=Query)
