# -*-coding:utf8-*-
from app.constants.bank_config_list import BANK_CONFIG_LIST
from app.extensions import db
from app.libs.model.base import ModelBase


class Bank(ModelBase):
    """
    记录银行卡的表
    """
    _create_time = db.Column('create_time', db.Integer, nullable=False, comment="创建时间", index=True)

    bank_name = db.Column(db.String(128), comment="银行名称例如中国工商银行")
    bank_code = db.Column(db.String(32), comment="银行简称例如ICBC")

    @classmethod
    def add_bank(cls, bank_name: str, bank_code: str):
        """
        添加日志
        :param bank_name:
        :param bank_code:
        :return:
        """
        with db.auto_commit():
            bank = cls()
            bank.bank_name = bank_name
            bank.bank_code = bank_code
            db.session.add(bank)

        return bank

    @classmethod
    def init_bank_data(cls):
        """
        初始化银行卡数据
        """
        # pattern = re.compile(r'bankName: "([^,]*)",\s*bankCode: "([^,]*)",')
        # ret1 = pattern.findall(BANK_JSON_STR)
        #
        # for item in ret1:
        #     print(item[0])
        #     Bank.add_bank(item[0], item[1])

        for item in BANK_CONFIG_LIST:
            cls.add_bank(item['bankName'], item['bankCode'])
