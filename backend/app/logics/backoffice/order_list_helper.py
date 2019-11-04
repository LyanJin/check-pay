"""
后台订单列表查询
"""
import functools
from operator import itemgetter

from app.caches.user_flag import UserFlagCache
from app.docs.doc_internal.trade_manage import AllWithdrawResult, DepositOrderResult
from app.libs.csv_kit import CsvKit
from app.libs.datetime_kit import DateTimeKit, DateTimeFormatEnum
from app.libs.error_code import MultiMonthQueryError
from app.libs.model.mix import MultiMonthQueryException
from app.libs.order_kit import OrderUtils
from app.logics.pagination.paginate_list import Pagination
from app.models.channel import ChannelConfig
from app.models.order.order import OrderWithdraw, OrderDeposit
from app.models.order.order_detail import OrderDetailWithdraw, OrderDetailDeposit


class CsvOrderExport:

    @classmethod
    def export_deposit_list_csv(cls, order_list, order_detail_dict, all_channels):
        """
        导出充值订单列表
        :param order_list:
        :param order_detail_dict:
        :param all_channels:
        :return:
        """
        # 用户id、系统订单号、商户订单号、创建时间、完成时间、商户、通道商户号、通道、发起金额、实际支付金额、优惠金额、手续费、
        # 成本金额、收入金额、订单状态、充值类型
        data = list()

        for order in order_list:
            channel = all_channels[order.channel_id]
            order_detail = order_detail_dict[order.order_id]

            data.append({
                "用户ID": order.uid,
                "系统订单号": order.sys_tx_id,
                "商户订单号": order.mch_tx_id,
                "创建时间": order.str_create_time,
                "完成时间": order_detail.str_done_time,
                "商户": order.merchant.name,
                "通道商户号": channel.channel_enum.conf['mch_id'],
                "通道": channel.channel_enum.desc,
                "发起金额": str(order.amount),
                "实际支付金额": str(order.tx_amount),
                "优惠金额": str(order_detail.offer),
                "手续费": str(order_detail.fee),
                "成本金额": str(order_detail.cost),
                "收入金额": str(order_detail.profit),
                "订单状态": order.state.desc,
                "充值类型": order.source.desc,
            })

        filename = 'epay_deposit_record_%s.csv' % DateTimeKit.datetime_to_str(
            DateTimeKit.get_cur_datetime(),
            DateTimeFormatEnum.TIGHT_DAY_FORMAT
        )
        return CsvKit.send_csv(data, filename=filename, fields=data[0].keys())

    @classmethod
    def export_withdraw_list_csv(cls, order_list, order_detail_dict, all_channels):
        """
        导出提现订单列表
        :param order_list:
        :param order_detail_dict:
        :param all_channels:
        :return:
        """
        # 用户id、系统订单号、商户订单号、创建时间、完成时间、商户、通道商户号、通道、提现金额、手续费、成本金额、收入金额、订单状态、出款类型、备注
        data = list()

        for order in order_list:
            channel = all_channels.get(order.channel_id)
            order_detail = order_detail_dict[order.order_id]
            data.append({
                "用户ID": order.uid,
                "系统订单号": order.sys_tx_id,
                "商户订单号": order.mch_tx_id,
                "创建时间": order.str_create_time,
                "完成时间": order_detail.str_done_time,
                "商户": order.merchant.name,
                "通道商户号": channel.channel_enum.conf['mch_id'] if channel else '',
                "通道": channel.channel_enum.desc if channel else '',
                "提现金额": str(order.amount),
                "手续费": str(order_detail.fee),
                "成本金额": str(order_detail.cost),
                "收入金额": str(order_detail.profit),
                "订单状态": order.state.desc,
                "出款类型": order.source.desc,
                "备注": order_detail.comment or '',
            })

        filename = 'epay_withdraw_record_%s.csv' % DateTimeKit.datetime_to_str(
            DateTimeKit.get_cur_datetime(),
            DateTimeFormatEnum.TIGHT_DAY_FORMAT
        )
        return CsvKit.send_csv(data, filename=filename, fields=data[0].keys())


class OrderFilters:

    @classmethod
    def filter_tx_id(cls, tx_id, order):
        """
        根据交易ID来过滤
        :param tx_id:
        :param order:
        :return: True: 过滤；False：不过滤
        """
        if not tx_id:
            return False

        if order.sys_tx_id == tx_id:
            return False

        if order.mch_tx_id == tx_id:
            return False

        return True

    @classmethod
    def filter_channel(cls, channel_dict, channel, order):
        """
        根据交易通道类型过滤
        :param channel_dict:
        :param channel:
        :param order:
        :return: True: 过滤；False：不过滤
        """
        if not channel:
            return False

        order_channel = channel_dict.get(order.channel_id)
        if not order_channel:
            return True

        if order_channel.channel_enum == channel:
            return False

        return True

    @classmethod
    def filter_done_time(cls, begin_time, end_time, order):
        """
        根据订单完成时间来过滤
        :param begin_time:
        :param end_time:
        :param order:
        :return: True: 过滤；False：不过滤
        """
        if order.done_time and begin_time and end_time:
            if order.done_time < begin_time or order.done_time > end_time:
                return True
        return False

    @classmethod
    def filter_from_order_list(cls, order_list, filters):
        """
        从订单列表中过滤
        :param order_list:
        :param filters:
        :return:
        """
        _order_list = list()

        for o in order_list:
            throw = False

            for filter_func in filters:
                if filter_func(o):
                    throw = True
                    break

            if not throw:
                _order_list.append(o)

        return _order_list

    @classmethod
    def filter_from_detail_list(cls, order_list, order_detail_list, filters):
        """
        需要从详情表里面过滤，订单列表和详情列表相互过滤
        :param order_list:
        :param order_detail_list:
        :param filters:
        :return:
        """
        order_detail_dict = dict()

        order_id_set = {o.order_id for o in order_list}

        for o in order_detail_list:
            if o.order_id not in order_id_set:
                # 把订单详情列表中不存在订单列表中的订单过滤
                continue

            throw = False

            for filter_func in filters:
                if filter_func(o):
                    throw = True
                    break

            if not throw:
                order_detail_dict[o.order_id] = o

        # 过滤订单列表中不存在订单详情列表的订单
        order_list = [o for o in order_list if o.order_id in order_detail_dict]

        return order_list, order_detail_dict


class OrderListQueryHelper:

    @classmethod
    def query_deposit_order_list(cls, form, export=False):
        """
        查询充值订单列表
        :param form:
        :param export:
        :return:
        """
        merchant = form.merchant_name.data

        if not form.begin_time.data:
            begin_time, end_time = DateTimeKit.get_day_begin_end(DateTimeKit.get_cur_date())
        else:
            begin_time = form.begin_time.data
            end_time = form.end_time.data

        kwargs = {}

        if form.state.data != "0":
            kwargs["_state"] = form.state.data.value

        tx_id = form.order_id.data
        if tx_id:
            if OrderUtils.is_sys_tx_id(tx_id):
                kwargs["sys_tx_id"] = tx_id
            else:
                kwargs["mch_tx_id"] = tx_id

        try:
            order_list = OrderDeposit.query_by_create_time(begin_time=begin_time, end_time=end_time,
                                                           merchant=merchant).filter_by(**kwargs)
        except MultiMonthQueryException:
            return MultiMonthQueryError().as_response()

        # 查询所有通道
        all_channels = dict([(x.channel_id, x) for x in ChannelConfig.query_all()])
        order_detail_dict = dict()
        order_list = OrderFilters.filter_from_order_list(order_list, filters=[
            functools.partial(OrderFilters.filter_tx_id, tx_id),
            functools.partial(OrderFilters.filter_channel, all_channels, form.channel.data),
        ])

        if order_list:
            # 订单详情列表
            order_detail_list = OrderDetailDeposit.query_by_create_time(begin_time=begin_time, end_time=end_time,
                                                                        merchant=merchant)

            # 订单列表和订单详情列表相互过滤
            order_list, order_detail_dict = OrderFilters.filter_from_detail_list(
                order_list, order_detail_list,
                filters=[
                    functools.partial(
                        OrderFilters.filter_done_time,
                        form.done_begin_time.data,
                        form.done_end_time.data),
                ])

            # 按时间倒序
            order_list = sorted(order_list, key=itemgetter('create_time'), reverse=True)

        if export and order_list:
            return CsvOrderExport.export_deposit_list_csv(order_list, order_detail_dict, all_channels)

        return cls.render_deposit_list(form, order_list, order_detail_dict, all_channels)

    @classmethod
    def render_deposit_list(cls, form, order_list, order_detail_dict, all_channels):
        # 分页
        order_list, total_count = Pagination.paginate_list(order_list, form.page_size.data, form.page_index.data)

        items = []
        for order in order_list:
            channel = all_channels[order.channel_id]
            order_detail = order_detail_dict[order.order_id]
            user_flag = UserFlagCache(order.uid).get_flag()
            items.append(dict(
                uid=order.uid,
                order_id=order.order_id,
                sys_tx_id=order.sys_tx_id,
                mch_tx_id=order.mch_tx_id,
                merchant=order.merchant.name,
                channel=channel.channel_enum.desc,
                mch_id=channel.channel_enum.conf['mch_id'],
                amount=order.amount,
                tx_amount=order.tx_amount,
                create_time=order.str_create_time,
                done_time=order_detail.str_done_time,
                state=order.state.get_back_desc(order.order_type),
                deliver=order.deliver.desc,
                user_flag=user_flag.name if user_flag else None,
            ))

        return DepositOrderResult(bs_data=dict(entries=items, total=total_count)).as_response()

    @classmethod
    def query_withdraw_order_list(cls, form, export=False):
        """
        查询提现订单列表
        :param form:
        :param export:
        :return:
        """

        merchant = form.merchant_name.data

        if not form.begin_time.data:
            begin_time, end_time = DateTimeKit.get_day_begin_end(DateTimeKit.get_cur_date())
        else:
            begin_time = form.begin_time.data
            end_time = form.end_time.data

        kwargs = {}
        if form.state.data != "0":
            kwargs["_state"] = form.state.data.value

        tx_id = form.order_id.data
        if tx_id:
            if OrderUtils.is_sys_tx_id(tx_id):
                kwargs["sys_tx_id"] = tx_id
            else:
                kwargs["mch_tx_id"] = tx_id

        try:
            order_list = OrderWithdraw.query_by_create_time(begin_time=begin_time, end_time=end_time,
                                                            merchant=merchant).filter_by(**kwargs)
        except MultiMonthQueryException:
            return MultiMonthQueryError().as_response()

        all_channels = dict([(x.channel_id, x) for x in ChannelConfig.query_all()])
        order_detail_dict = dict()

        order_list = OrderFilters.filter_from_order_list(order_list, filters=[
            functools.partial(OrderFilters.filter_tx_id, tx_id),
            functools.partial(OrderFilters.filter_channel, all_channels, form.channel.data),
        ])

        if order_list:
            # 订单详情列表
            order_detail_list = OrderDetailWithdraw.query_by_create_time(begin_time=begin_time, end_time=end_time,
                                                                         merchant=merchant)

            # 订单列表和订单详情列表相互过滤
            order_list, order_detail_dict = OrderFilters.filter_from_detail_list(
                order_list, order_detail_list,
                filters=[
                    functools.partial(
                        OrderFilters.filter_done_time,
                        form.done_begin_time.data,
                        form.done_end_time.data),
                ])

            # 按时间倒序
            order_list = sorted(order_list, key=itemgetter('create_time'), reverse=True)

        if export and order_list:
            return CsvOrderExport.export_withdraw_list_csv(order_list, order_detail_dict, all_channels)

        return cls.render_withdraw_list(form, order_list, order_detail_dict)

    @classmethod
    def render_withdraw_list(cls, form, order_list, order_detail_dict):

        # 分页
        order_list, total_count = Pagination.paginate_list(order_list, form.page_size.data, form.page_index.data)

        items = []
        for order in order_list:
            order_detail = order_detail_dict[order.order_id]
            user_flag = UserFlagCache(order.uid).get_flag()

            items.append(dict(
                uid=order.uid,
                order_id=order.order_id,
                sys_tx_id=order.sys_tx_id,
                mch_tx_id=order.mch_tx_id,
                merchant=order.merchant.name,
                source=order.source.desc,
                amount=order.amount,
                create_time=order.create_time,
                done_time=order_detail.str_done_time,
                state=order.state.get_back_desc(order.order_type),
                operator=order_detail.op_account,
                deliver=order.deliver.desc,
                user_flag=user_flag.name if user_flag else None,
            ))

        return AllWithdrawResult(bs_data=dict(entries=items, total=total_count)).as_response()
