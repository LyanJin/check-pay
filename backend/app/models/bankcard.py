"""
用户银行卡信息
"""
from app.enums.trade import PaymentBankEnum
from app.extensions import db
from app.libs.model.base import MerchantBase
from config import MerchantEnum


# @MerchantBase.init_models
class BankCard(MerchantBase):
    """
    用户银行卡表，按商户分库
    """
    # __abstract__ = True

    valid = db.Column(db.SmallInteger, comment='是否删除', nullable=False)
    uid = db.Column(db.Integer, comment='用户ID', nullable=False)
    bank_name = db.Column(db.String(128), comment="银行名称例如中国工商银行", nullable=False)
    bank_code = db.Column(db.String(32), comment="银行简称例如ICBC", nullable=False)
    card_no = db.Column(db.String(32), comment="银行卡卡号例如：6212260405014627955", nullable=False)
    account_name = db.Column(db.String(20), comment="开户人姓名例如：张三", nullable=False)
    branch = db.Column(db.String(100), comment="支行名称例如：广东东莞东莞市长安镇支行", nullable=True)
    province = db.Column(db.String(32), comment="省份 例如：湖北省", nullable=False)
    city = db.Column(db.String(32), comment="市 例如：深圳市", nullable=False)

    __table_args__ = (
        # 联合唯一索引
        db.UniqueConstraint('card_no', 'merchant', name='uix_bank_card_no_merchant'),
        # 联合索引
        # db.Index('ix_user_account_mch_name', 'account', 'merchant'),
    )

    _merchant = db.Column('merchant', db.Integer, comment="商户ID", nullable=False)

    @property
    def merchant(self) -> MerchantEnum:
        return MerchantEnum(self._merchant)

    @merchant.setter
    def merchant(self, merchant: MerchantEnum):
        self._merchant = merchant.value

    @property
    def bank_enum(self):
        return PaymentBankEnum.get_bank_by_code(self.bank_code)

    @property
    def card_id(self):
        return self.id

    @property
    def short_description(self):
        return self.bank_name + '(' + self.card_no[-4:] + ')' + ' *' + self.account_name[1:]

    @property
    def card_no_short_description(self):
        card_hide = "**** **** **** {}".format(self.card_no[-4:])
        # card_list = [self.card_no[index:index + 4] for index in range(0, len(self.card_no), 4)]
        # card_hide = ""
        # for index, num in enumerate(card_list):
        #     if index != len(card_list)-1:
        #         card_hide += "**** "
        #     else:
        #         card_hide += "{}".format(num)
        return card_hide

    @property
    def bank_address(self):
        return (self.province or '') + (self.city or '') + (self.branch or '')

    @classmethod
    def generate_model(cls, **kwargs):
        bank_card = cls.get_model_obj()
        bank_card.set_attr(kwargs)
        return bank_card

    @property
    def bank_info_dict(self):
        return dict(
            bank_name=self.bank_name,
            bank_code=self.bank_code,
            card_no=self.card_no,
            account_name=self.account_name,
            branch=self.branch,
            province=self.province,
            city=self.city,
        )

    @classmethod
    def add_bank_card(cls, merchant: MerchantEnum, uid: int, bank_name: str, bank_code: str, card_no: str,
                      account_name: str, branch: str, province: str, city: str):
        """
        添加用户银行卡
        :param merchant:
        :param uid:
        :param bank_name:
        :param bank_code:
        :param card_no:
        :param account_name:
        :param branch:
        :param province:
        :param city:
        :return:
        """
        with db.auto_commit():
            bank_card = cls.query_one(query_fields=dict(card_no=card_no, valid=cls.INVALID, _merchant=merchant.value))
            if not bank_card:
                bank_card = cls.get_model_obj(merchant=merchant)
            bank_card.valid = cls.VALID
            bank_card.uid = uid
            bank_card.bank_name = bank_name
            bank_card.bank_code = bank_code
            bank_card.card_no = card_no
            bank_card.account_name = account_name
            bank_card.branch = branch
            bank_card.province = province
            bank_card.city = city
            bank_card.merchant = merchant
            db.session.add(bank_card)

        return bank_card

    @classmethod
    def delete_bankcard_by_card_no(cls, merchant, card_no):
        """
        根据卡号删除用户银行卡
        :param merchant:
        :param card_no:
        :return:
        """
        with db.auto_commit():
            bank_card = cls.query_bankcard_by_card_no(merchant, card_no=card_no)
            bank_card.valid = cls.INVALID
            db.session.add(bank_card)

    @classmethod
    def delete_bankcard_by_card_id(cls, card_id):
        """
        根据卡号删除用户银行卡
        :param card_id:
        :return:
        """
        with db.auto_commit():
            bank_card = cls.query_bankcard_by_id(card_id=card_id)
            bank_card.valid = cls.INVALID
            db.session.add(bank_card)

    @classmethod
    def query_bankcard_by_card_no(cls, merchant, card_no):
        """
        根据卡号查询用户银行卡记录
        :param merchant:
        :param card_no:
        :return:
        """
        kwargs = dict(card_no=str(card_no), valid=cls.VALID, _merchant=merchant.value)
        return cls.query_one(query_fields=kwargs)

    @classmethod
    def query_bankcard_by_id(cls, card_id, valid_check=True):
        """
        根据卡id查询用户银行卡记录
        :param card_id:
        :param valid_check:
        :return:
        """
        if valid_check:
            kwargs = dict(id=str(card_id), valid=cls.VALID)
        else:
            kwargs = dict(id=str(card_id))
        return cls.query_one(query_fields=kwargs)

    @classmethod
    def query_bankcards_by_uid(cls, merchant, uid):
        """
        根据卡号查询用户银行卡记录
        :param merchant:
        :param uid:
        :return:
        """
        kwargs = dict(uid=int(uid), valid=cls.VALID)
        return cls.query_model(query_fields=kwargs, merchant=merchant).order_by(cls._create_time.desc()).all()

    @classmethod
    def query_bankcards_by_bank_ids(cls, merchant, bank_ids):
        """
        查询一批银行卡的信息
        :param merchant:
        :param bank_ids:
        :return:
        """
        model_cls = cls.get_model_cls(merchant=merchant)
        return model_cls.query.filter(model_cls.id.in_(bank_ids))
