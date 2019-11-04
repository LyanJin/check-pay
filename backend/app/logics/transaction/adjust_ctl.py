from app.extensions import db
from app.libs.api_exception import APIException
from flask import current_app
import traceback
import copy

from app.libs.error_code import DepositCallbackUserBalanceError, AdjustUserBalanceError
from app.libs.order_kit import OrderUtils
from app.models.balance import UserBalanceEvent
from app.models.merchant import MerchantBalanceEvent


class AdjustTransactionCtl:

    @staticmethod
    def adjust_create(user, source, amount, bl_type, order_type, ad_type, comment, tx_id=None, ref_id=None):

        params = copy.deepcopy(locals())
        # params.pop('cls')

        adjust_flag = True

        try:
            # 更新商户及用户余额
            with db.auto_commit():
                if not tx_id:
                    tx_id = OrderUtils.gen_normal_tx_id(user.uid)

                if not ref_id:
                    ref_id = OrderUtils.gen_unique_ref_id()
                # 更新用户余额
                flag, msg = UserBalanceEvent.update_user_balance(uid=user.uid,
                                                                 merchant=user.merchant,
                                                                 ref_id=ref_id,
                                                                 source=source,
                                                                 order_type=order_type,
                                                                 bl_type=bl_type,
                                                                 value=amount,
                                                                 ad_type=ad_type,
                                                                 tx_id=tx_id,
                                                                 comment=comment,
                                                                 commit=False,
                                                                 )
                if flag < 0:
                    msg = '%s, params: %s' % ("更新用户余额失败, %s" % msg, params)
                    current_app.logger.error(msg)
                    raise AdjustUserBalanceError(message="更新用户余额失败")

                # 更新商户余额
                flag, msg = MerchantBalanceEvent.update_balance(merchant=user.merchant,
                                                                ref_id=ref_id,
                                                                source=source,
                                                                order_type=order_type,
                                                                bl_type=bl_type,
                                                                value=amount,
                                                                ad_type=ad_type,
                                                                tx_id=tx_id,
                                                                comment=comment,
                                                                commit=False,
                                                                )
                if flag < 0:
                    msg = '%s, params: %s' % ("更新商户余额失败, %s" % msg, params)
                    current_app.logger.error(msg)
                    raise AdjustUserBalanceError(message="更新商户余额失败")

        except APIException as e:
            current_app.logger.error(traceback.format_exc())
            adjust_flag = False
            return adjust_flag, e

        return adjust_flag, None
