<template>
  <main>
    <main class="fillcontain clear" v-if="this.$route.name == 'payOrder'">
      <section class="main">
        <el-form
          ref="opyOrderForm"
          :model="opyOrderForm"
          label-width="80px"
          size="mini"
        >
          <!-- 筛选条件 -->
          <!-- <el-form-item label="商户">
            <el-select v-model="opyOrderForm.name" placeholder="请选择">
              <el-option
                v-for="item in merchant_names"
                :key="item.name"
                :label="item.name"
                :value="item.name"
              >
              </el-option>
            </el-select>
          </el-form-item> -->

          <el-form-item label="订单号" label-width="90px">
            <el-input
              v-model="opyOrderForm.order_id"
              placeholder="请输入内容"
              maxlength="40"
              clearable
            ></el-input>
          </el-form-item>

          <el-form-item label="订单时间">
            <el-date-picker
              v-model="opyOrderForm.optionTime"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              :picker-options="pickerOptions"
              :clearable="false"
              :default-time="defaultTime"
            >
            </el-date-picker>
          </el-form-item>

          <!-- <el-form-item label="用户ID">
          <el-input
            v-model="input"
            placeholder="请输入内容"
            clearable
          ></el-input>
        </el-form-item>

        <el-form-item label="订单金额" class="money">
          <el-input v-model="input" placeholder="请输入" clearable></el-input>
          -
          <el-input v-model="input" placeholder="请输入" clearable></el-input>
        </el-form-item>

        <el-form-item label="通道">
          <el-select v-model="form.value" placeholder="请选择" clearable>
            <el-option
              v-for="item in options"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            >
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="来源">
          <el-select v-model="form.value" placeholder="请选择" clearable>
            <el-option
              v-for="item in options"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            >
            </el-option>
          </el-select>
        </el-form-item> -->

          <el-form-item>
            <el-button type="primary" @click="onSubmit">查询</el-button>
          </el-form-item>
        </el-form>
      </section>

      <!-- 充值订单展示列表 -->

      <section class="main">
        <el-radio-group v-model="activeName" size="medium">
          <el-radio-button label="0">全部</el-radio-button>
          <el-radio-button label="10">未支付</el-radio-button>
          <el-radio-button label="30">充值成功</el-radio-button>
          <el-radio-button label="40">充值失败</el-radio-button>
        </el-radio-group>

        <el-button class="el-icon-download download" @click="load"></el-button>

        <el-table
          :data="tableData"
          :header-row-style="{
            color: '#333'
          }"
        >
          <!-- <el-table-column align="center" prop="uid" label="用户ID" width="80">
          </el-table-column> -->
          <el-table-column align="center" prop="mch_tx_id" label="商户订单号">
          </el-table-column>
          <!-- <el-table-column align="center" prop="sys_tx_id" label="系统订单号">
          </el-table-column> -->
          <!-- <el-table-column align="center" prop="merchant" label="商户"> </el-table-column> -->
          <!-- <el-table-column align="center" prop="mch_id" label="通道商户号"> </el-table-column>
          <el-table-column align="center" prop="channel" label="通道"> </el-table-column> -->
          <el-table-column align="center" label="发起金额">
            <div slot-scope="scope">
              {{ scope.row.amount | NumFormat }}
            </div>
          </el-table-column>
          <el-table-column align="center" label="手续费">
            <div slot-scope="scope">
              {{ scope.row.fee | NumFormat }}
            </div>
          </el-table-column>
          <el-table-column align="center" label="实际支付金额">
            <div slot-scope="scope">
              {{ scope.row.tx_amount | NumFormat }}
            </div>
          </el-table-column>
          <el-table-column
            align="center"
            prop="create_time"
            sortable
            label="创建时间"
          >
          </el-table-column>
          <el-table-column
            align="center"
            prop="done_time"
            sortable
            label="完成时间"
          >
          </el-table-column>
          <el-table-column
            align="center"
            prop="state"
            label="订单状态"
            width="80"
          >
          </el-table-column>
          <el-table-column
            align="center"
            prop="deliver"
            label="通知状态"
            width="80"
          >
          </el-table-column>
          <el-table-column align="center" fixed="right" label="操作">
            <div slot-scope="scope">
              <!-- <el-button @click="detailClick(scope.row)" type="text">
                详情
              </el-button> -->
              <el-button
                v-if="scope.row.deliver != '通知成功'"
                @click="orderNotify(scope.row)"
                type="text"
              >
                补发通知
              </el-button>
            </div>
          </el-table-column>
        </el-table>
        <!-- 分页 -->
        <el-pagination
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-size="10"
          layout="total, prev, pager, next, jumper"
          :total="total"
          style="margin-top: 20px;text-align: center;"
        >
        </el-pagination>
      </section>
    </main>

    <keep-alive v-else>
      <router-view></router-view>
    </keep-alive>
  </main>
</template>

<script>
import { orderDeposit, tradeRefuseOrderNotify, orderDepositCsv } from '../../api/getData'

export default {
  data () {
    return {
      activeName: '0', //默认显示全部
      total: null,           //列表总数
      tableData: null,       //订单列表
      currentPage: 1,        //页数
      merchant_names: null,  //商户列表
      pickerOptions: { //设置只能查看前三个月
        disabledDate (time) {
          let curDate = (new Date()).getTime();
          let three = 90 * 24 * 3600 * 1000;
          let threeMonths = curDate - three;
          return time.getTime() > (Date.now() + 24 * 3600 * 1000) || time.getTime() < threeMonths
        },
      },
      defaultTime: ['00:00:00', '23:59:59'],
      // 筛选条件列表
      opyOrderForm: {
        name: '', //商户
        order_id: null,  //订单id
        // 默认当前时间
        optionTime: [
          new Date(new Date().getFullYear(), new Date().getMonth(), new Date().getDate()),  //开始时间
          new Date()        //截止时间
        ],
      },
    }
  },

  async activated () {
    // 筛选功能获取商户配置信息
    // const config = await configGetunt()
    // if (config) {
    //   // 设置商户
    //   this.opyOrderForm.name = config.data.merchant_names[0].name
    //   // 设置商户列表
    //   this.merchant_names = config.data.merchant_names
    // }
    this.opyOrderForm.optionTime = [
      new Date(new Date().getFullYear(), new Date().getMonth(), new Date().getDate()),  //开始时间
      new Date()        //截止时间
    ]
    this.init()
  },
  methods: {
    // 获取充值订单列表
    async init () {
      if (!this.opyOrderForm.optionTime) {
        this.$message({
          showClose: true,
          message: '订单时间不能为空！',
          type: 'error'
        });
        return
      }
      this.withdrawList = {
        order_id: this.opyOrderForm.order_id,
        page_size: 10,
        page_index: this.currentPage,
        start_datetime: this.getTime(this.opyOrderForm.optionTime[0]),
        end_datetime: this.getTime(this.opyOrderForm.optionTime[1]),
        state: this.activeName
      }
      const data = await orderDeposit(this.withdrawList)
      if (data) {
        this.tableData = data.data.entries
        this.total = Number(data.data.total)
      }

    },
    //筛选
    onSubmit () {
      this.currentPage = 1
      this.init()
    },
    // 时间转换
    getTime (data) {
      let Y = data.getFullYear() + '-';
      let M = (data.getMonth() + 1 < 10 ? '0' + (data.getMonth() + 1) : data.getMonth() + 1) + '-';
      let D = data.getDate() + ' ';
      let h = data.getHours() + ':';
      let m = data.getMinutes() + ':';
      let s = data.getSeconds();
      return Y + M + D + h + m + s
    },
    // // 查看订单详情
    // detailClick (data) {
    //   console.log(data)
    //   data.page = "payOrder"
    //   this.$router.push({ name: 'orderDetails', params: { restaurant_id: data } })
    // },

    // 补发通知
    async orderNotify (item) {
      const data = await tradeRefuseOrderNotify({ order_id: item.sys_tx_id, type: '1' })
      if (data && data.message) {
        this.$notify.info({
          title: '消息',
          message: data.message
        });
      }
    },

    // 分页
    handleCurrentChange (val) {
      this.currentPage = val
      this.init()
    },
    // 下载订单
    async load () {
      const data = await orderDepositCsv(this.withdrawList)
      if (data) {
        console.warn(data)
      }
    }

  },
  watch: {
    activeName: function () {
      this.init()
    },
  }
}
</script>

<style lang="less" scoped>
@import "../../style/mixin";
.fillcontain {
  .main {
    .el-form-item {
      display: inline-block;
      margin-bottom: 12px;
    }
    .money {
      .el-input {
        width: 40%;
      }
    }
    .download {
      font-size: 1.3rem;
      padding: 6px 10px;
      float: right;
      margin-right: 5rem;
      margin-top: 0.1rem;
    }
  }
  .el-form-item {
    display: inline-block;
  }
}
</style>


