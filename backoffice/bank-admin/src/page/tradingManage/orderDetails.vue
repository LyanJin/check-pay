<template>
  <main class="fillcontain" v-if="orderData">
    <section class="orderTime">
      <h3>
        <i class="el-icon-s-order"></i> 系统单号：
        {{ orderData.detail_head.sys_tx_id }}
      </h3>
      <ul class="table-state">
        <li v-if="orderData.detail_head.op_account">
          操作员：<em>{{ orderData.detail_head.op_account }}</em>
        </li>
        <li v-if="orderData.detail_head.deliver_type">
          出款类型：<em>{{ orderData.detail_head.deliver_type }}</em>
        </li>
        <li v-if="orderData.detail_head.source">
          充值类型：<em>{{ orderData.detail_head.source }}</em>
        </li>
        <li v-if="orderData.detail_head.settle_type">
          结算状态：<em>{{ orderData.detail_head.settle_type }}</em>
        </li>
        <li v-if="orderData.detail_head.create_time">
          创建时间：<em>{{ orderData.detail_head.create_time }}</em>
        </li>
        <li v-if="orderData.detail_head.alloc_time">
          认领时间：<em>{{ orderData.detail_head.alloc_time }}</em>
        </li>
        <li v-if="orderData.detail_head.deal_time">
          处理时间：<em>{{ orderData.detail_head.deal_time }}</em>
        </li>
        <li v-if="orderData.detail_head.done_time">
          完成时间：<em>{{ orderData.detail_head.done_time }}</em>
        </li>
        <li v-if="orderData.detail_head.mch_tx_id">
          商户订单号：<em>{{ orderData.detail_head.mch_tx_id }}</em>
        </li>
        <li v-if="orderData.detail_head.settle">
          结算状态：<em>{{ orderData.detail_head.settle }}</em>
        </li>
        <li v-if="orderData.detail_head.deliver">
          通知状态：<em>{{ orderData.detail_head.deliver }}</em>
        </li>
      </ul>
      <div class="state-money">
        <div>
          <p>订单状态</p>
          <h3>{{ orderData.detail_head.state }}</h3>
        </div>
        <div>
          <p>实际支付金额</p>
          <h3>{{ orderData.detail_head.amount | NumFormat }}</h3>
        </div>
      </div>
    </section>

    <!-- 订单信息 -->
    <section class="orderInfo">
      <h3>订单信息</h3>
      <div class="orderbox">
        <ul>
          <li v-if="orderData.order_merchant_info.merchant_name">
            商户名称：
            <span> {{ orderData.order_merchant_info.merchant_name }}</span>
          </li>
          <li v-if="orderData.order_merchant_info.fee">
            手续费：<span> {{ orderData.order_merchant_info.fee }}</span>
          </li>
          <li v-if="orderData.order_merchant_info.offer">
            优惠金额：<span> {{ orderData.order_merchant_info.offer }}</span>
          </li>
          <li v-if="orderData.order_merchant_info.cost">
            成本金额：<span> {{ orderData.order_merchant_info.cost }}</span>
          </li>
          <li v-if="orderData.order_merchant_info.profit">
            收入金额：<span> {{ orderData.order_merchant_info.profit }}</span>
          </li>
          <li v-if="orderData.order_merchant_info.withdraw_type">
            类型：
            <span> {{ orderData.order_merchant_info.withdraw_type }}</span>
          </li>
        </ul>

        <h4 v-if="page == 'payOrder'">
          通道信息
        </h4>
        <h4 v-else>出款信息</h4>
        <ul>
          <li>
            通道：<span> {{ orderData.deliver_info.channel_name }}</span>
          </li>
          <li>
            通道商户号：<span> {{ orderData.deliver_info.mch_id }}</span>
          </li>
          <li>
            通道订单号：<span> {{ orderData.deliver_info.channel_tx_id }}</span>
          </li>
        </ul>
        <h4>用户信息</h4>
        <ul>
          <li>
            用户ID：<span> {{ orderData.user_info.user_id }}</span>
          </li>
          <li>
            地区：<span> {{ orderData.user_info.location }}</span>
          </li>
          <li>
            IP：<span> {{ orderData.user_info.ip }}</span>
          </li>
          <li v-if="orderData.user_info.device">
            设备：<span> {{ orderData.user_info.device }}</span>
          </li>
        </ul>
      </div>
    </section>

    <section class="orderInfo">
      <h3>操作日志</h3>
      <el-table
        :data="orderData.event_log_list"
        :header-row-style="{
          color: '#333'
        }"
      >
        <el-table-column align="center" prop="operate_type" label="操作类型">
        </el-table-column>
        <el-table-column align="center" prop="operator" label="操作员">
        </el-table-column>
        <el-table-column align="center" prop="result" label="执行结果">
        </el-table-column>
        <el-table-column align="center" prop="operate_time" label="操作时间">
        </el-table-column>
        <el-table-column align="center" prop="comment" label="备注">
        </el-table-column>
      </el-table>
    </section>
  </main>
</template>

<script >
import { tradeOrderDetail, depositOrderDetail } from '../../api/getData'

export default {
  data () {
    return {
      orderData: null,
      page: null   //判断页面类型
    }
  },

  async activated () {
    if (this.$route.params.restaurant_id) {
      // 获取页面类型
      if (this.$route.params.restaurant_id.page) {
        this.page = this.$route.params.restaurant_id.page
      }

      let params = {
        order_id: this.$route.params.restaurant_id.order_id,
        merchant: this.$route.params.restaurant_id.merchant
      }
      let data = null
      if (this.page == "withdrawalOrder") {
        // 提现订单详情
        data = await tradeOrderDetail(params)
      } else {
        // 充值订单详情
        data = await depositOrderDetail(params)
      }
      if (data) {
        this.orderData = data.data
        console.warn(this.orderData)
      }
    } else {
      this.$router.go(-1)
    }

  },
  methods: {

  },
}
</script>

<style lang="less" scoped>
@import "../../style/mixin";
.fillcontain {
  background: #f4f4f4;
  .orderTime {
    background: #fff;
    padding: 20px;
    h3 {
      padding-bottom: 20px;
    }
    .el-icon-s-order {
      color: #409eff;
    }
    .table-state {
      display: inline-block;
      width: 75%;
      font-size: 14px;
      padding-left: 20px;
      box-sizing: border-box;
      vertical-align: top;
      li {
        display: inline-block;
        width: 33%;
        line-height: 24px;
        em {
          color: #666;
          word-wrap: break-word;
        }
      }
    }
    .state-money {
      display: inline-block;
      width: 24%;
      p {
        color: #999;
        font-size: 14px;
      }
    }
  }
  .orderInfo {
    background: #fff;
    margin: 20px;
    h3 {
      padding: 10px 20px;
      border-bottom: 1px solid #ddd;
    }
    .orderbox {
      padding: 10px 20px;
      ul {
        padding-bottom: 20px;
        li {
          display: inline-block;
          width: 33%;
          line-height: 30px;
          font-size: 14px;
        }
      }
    }
  }
}
</style>


