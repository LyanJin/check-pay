<template>
  <main>
    <main
      id="withdrawalOrder"
      class="fillcontain clear"
      v-if="this.$route.name == 'withdrawalOrder'"
    >
      <section class="main">
        <el-form
          ref="form"
          :model="withdrawalForm"
          label-width="80px"
          size="mini"
        >
          <!-- 筛选条件 -->
          <el-form-item label="商户">
            <el-select
              v-model="withdrawalForm.name"
              clearable
              placeholder="请选择"
            >
              <el-option
                v-for="item in config.merchant_names"
                :key="item.name"
                :label="item.name"
                :value="item.name"
              >
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="订单号" label-width="90px">
            <el-input
              v-model="withdrawalForm.order_id"
              placeholder="请输入内容"
              maxlength="40"
              clearable
            ></el-input>
          </el-form-item>

          <el-form-item label="订单时间">
            <el-date-picker
              v-model="withdrawalForm.optionTime"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              :picker-options="pickerOptions"
              :clearable="false"
              :default-time="['00:00:00', '23:59:59']"
            >
            </el-date-picker>
          </el-form-item>

          <el-form-item label="通道">
            <el-select
              v-model="withdrawalForm.channel"
              placeholder="请选择"
              clearable
            >
              <el-option
                v-for="item in config.channels_withdraw"
                :key="item.name"
                :label="item.desc"
                :value="item.name"
              >
              </el-option>
            </el-select>
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

      <!-- 提现订单展示列表 -->

      <section class="main">
        <el-radio-group v-model="activeName" size="medium">
          <el-radio-button label="0">全部</el-radio-button>
          <el-badge
            :value="newOrder"
            :hidden="newOrder == 0 ? true : false"
            :max="99"
            class="item"
          >
            <el-radio-button label="10">待认领</el-radio-button>
          </el-badge>
          <el-radio-button label="20">已认领</el-radio-button>
          <el-radio-button label="21">处理中</el-radio-button>
          <el-radio-button label="30">提现成功</el-radio-button>
          <el-radio-button label="40">提现失败</el-radio-button>
        </el-radio-group>

        <el-button class="el-icon-download download" @click="load"></el-button>

        <el-button type="primary" class="right refresh" @click="onRefresh">
          <i
            :class="{
              'el-icon-refresh': download,
              'el-icon-loading': !download
            }"
          ></i>
          刷新
        </el-button>
        <el-table
          :data="tableData"
          :header-row-style="{
            color: '#333'
          }"
          :row-class-name="tableRowClassName"
          v-loading="!download"
        >
          <el-table-column align="center" prop="uid" label="用户ID" width="100">
          </el-table-column>
          <el-table-column
            align="center"
            prop="mch_tx_id"
            label="商户订单号"
            width="190"
          >
          </el-table-column>
          <el-table-column
            align="center"
            prop="sys_tx_id"
            label="系统订单号"
            width="190"
          >
          </el-table-column>
          <el-table-column align="center" prop="merchant" label="商户">
          </el-table-column>
          <el-table-column align="center" label="提现金额">
            <div slot-scope="scope">
              {{ scope.row.amount | NumFormat }}
            </div>
          </el-table-column>
          <el-table-column
            align="center"
            prop="create_time"
            sortable
            label="创建时间"
            width="165"
          ></el-table-column>

          <el-table-column
            align="center"
            prop="state"
            label="订单状态"
          ></el-table-column>

          <el-table-column
            align="center"
            prop="deliver"
            label="通知状态"
            width="80"
          >
          </el-table-column>

          <el-table-column
            align="center"
            prop="operator"
            label="操作员"
          ></el-table-column>

          <el-table-column fixed="right" label="操作" width="160">
            <div slot-scope="scope">
              <el-button
                type="text"
                v-if="scope.row.state == '待认领'"
                @click="tradeOrder(scope.row)"
              >
                认领
              </el-button>

              <el-button @click="detailClick(scope.row)" type="text">
                详情
              </el-button>

              <el-button
                type="text"
                v-if="scope.row.state == '提现成功'"
                @click="refused(scope.row)"
              >
                退款
              </el-button>
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
import { mapMutations, mapState } from 'vuex'
import { tradeWithdrawList, configGetunt, tradeRefuseOrderNotify, tradeOrderAllowed, tradeRefuseReimburse, tradeWithdrawListExport } from '@/api/getData'
import { getLocalStore, getTimeForm } from '@/config/mUtils'
import { setTimeout } from 'timers';

export default {
  data () {
    return {
      activeName: '0',       //默认显示全部
      total: null,           //列表总数
      tableData: null,       //订单列表
      currentPage: 1,        //页数
      config: {},            //配置列表
      download: true,        //刷新按钮icon
      //设置只能查看前三个月
      pickerOptions: {
        disabledDate (time) {
          let curDate = (new Date()).getTime();
          let three = 90 * 24 * 3600 * 1000;
          let threeMonths = curDate - three;
          return time.getTime() > (Date.now() + 24 * 3600 * 1000) || time.getTime() < threeMonths;
        }
      },

      // 筛选条件列表
      withdrawalForm: {
        name: '', //商户
        order_id: null,  //订单id
        // 默认当前时间
        optionTime: [
          new Date(new Date().getFullYear(), new Date().getMonth(), new Date().getDate()),  //开始时间
          new Date()        //截止时间
        ],
      },

      // 列表参数
      withdrawList: {
        order_id: null,
        merchant_name: null,
        page_size: 10,
        page_index: 1,
        begin_time: new Date(new Date().getFullYear(), new Date().getMonth(), new Date().getDate()),
        end_time: new Date(),
        state: "0"
      },

    }
  },

  async activated () {
    // 筛选功能获取商户配置信息
    const config = await configGetunt()
    if (config) {
      // 设置商户
      // this.withdrawalForm.name = config.data.config[0].name
      // 设置商户列表
      this.config = config.data
    }
    this.withdrawalForm.optionTime = [
      new Date(new Date().getFullYear(), new Date().getMonth(), new Date().getDate()),  //开始时间
      new Date()        //截止时间
    ]
    this.init()
  },
  computed: {
    ...mapState([
      'newOrder'
    ]),
  },
  methods: {
    ...mapMutations([
      'NEW_ORDER'
    ]),
    // 获取提现订单列表
    async init () {
      this.download = false
      // 超时处理
      setTimeout(() => {
        if (!this.download) {
          console.warn('8秒后关闭download')
          this.download = true
        }
      }, 8000);
      if (!this.withdrawalForm.optionTime) {
        this.$message({
          showClose: true,
          message: '订单时间不能为空！',
          type: 'error'
        });
        return
      }
      this.withdrawList = {
        order_id: this.withdrawalForm.order_id,
        merchant_name: this.withdrawalForm.name,
        channel: this.withdrawalForm.channel,
        page_size: 10,
        page_index: this.currentPage,
        begin_time: getTimeForm(this.withdrawalForm.optionTime[0]),
        end_time: getTimeForm(this.withdrawalForm.optionTime[1]),
        state: this.activeName
      }
      const data = await tradeWithdrawList(this.withdrawList)
      if (data) {
        this.tableData = data.data.entries
        this.total = Number(data.data.total)
        if (this.activeName == 10) {
          this.NEW_ORDER(this.total)
        }
        setTimeout(() => {
          this.download = true
        }, 300)
      }

    },
    //筛选
    onSubmit () {
      this.currentPage = 1
      this.init()
    },
    // 查看订单详情
    detailClick (data) {
      console.warn(data)
      data.page = "withdrawalOrder"
      this.$router.push({ name: 'TorderDetails', params: { restaurant_id: data } })
    },

    // 补发通知
    async orderNotify (item) {
      const data = await tradeRefuseOrderNotify({ order_id: item.order_id, order_type: 'WITHDRAW' })
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
    // 人工补单
    fillOrder () {
      this.$router.push({ path: 'fillOrder' })
    },
    // 认领订单
    async tradeOrder (item) {
      let params = {
        order_id: item.order_id,
        merchant_name: item.merchant
      }
      const data = await tradeOrderAllowed(params)
      if (data) {
        item.state = '处理中'
        let reduce = this.newOrder - 1
        this.NEW_ORDER(reduce)
        item.operator = getLocalStore('username')
      }
    },
    // 退款
    async refused (item) {
      this.$confirm('是否确定退款，该操作将商户和用户增加对应的金额。', '退款确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.tradeRefuseReimburse(item)
      }).catch(() => { });
    },
    async tradeRefuseReimburse (item) {
      let params = {
        order_id: item.order_id,
        merchant: item.merchant
      }
      const data = await tradeRefuseReimburse(params)
      if (data) {
        item.state = '提现失败'
        item.operator = getLocalStore('username')
      }
    },
    // 下载订单
    async load () {
      const data = await tradeWithdrawListExport(this.withdrawList)
      if (data) {
        console.warn(data)
      }
    },
    //刷新列表数据
    async onRefresh () {
      // 更新待认领角标
      this.withdrawList.end_time = getTimeForm(new Date())
      this.withdrawList.state = '10'
      const data = await tradeWithdrawList(this.withdrawList)
      if (data) {
        if (data.data.total) {
          console.warn(data.data.total)
          // 更新提现订单数
          this.NEW_ORDER(data.data.total)
        }
      }

      // 更新当前列表
      this.withdrawalForm.optionTime = [
        new Date(new Date().getFullYear(), new Date().getMonth(), new Date().getDate()),  //开始时间
        new Date()        //截止时间
      ]
      this.init()
    },
    // 列表用户是否VIP改变样式
    tableRowClassName ({ row }) {
      if (row.user_flag == 'VIP') {
        return 'vip-row';
      }
      return '';
    },
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
    .refresh {
      margin-right: 80px;
    }
  }
  .el-form-item {
    display: inline-block;
  }
}
</style>
<style lang="less">
#withdrawalOrder {
  .is-fixed {
    z-index: 1;
  }
  .el-radio-button__inner {
    border-radius: inherit;
  }
}
</style>

