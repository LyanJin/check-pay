<template>
  <main>
    <main class="main" v-if="this.$route.name == 'withdrawalAudit'">
      <!-- 月份选择 -->
      <section class="block">
        <span>订单时间：</span>
        <el-date-picker
          v-model="time"
          :clearable="false"
          type="month"
          placeholder="选择月"
        >
        </el-date-picker>
      </section>

      <!-- 提现订单展示列表 -->
      <section class="main fillcontain">
        <el-table
          :data="tableData"
          :header-row-style="{
            color: '#333'
          }"
          :row-class-name="tableRowClassName"
        >
          <el-table-column align="center" prop="uid" label="用户ID" width="80">
          </el-table-column>
          <el-table-column align="center" prop="sys_tx_id" label="系统订单号">
          </el-table-column>
          <!-- <el-table-column align="center" prop="type" label="类型" width="100">
          </el-table-column> -->
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
          >
          </el-table-column>
          <el-table-column
            align="center"
            prop="bank_name"
            label="开户银行"
          ></el-table-column>
          <el-table-column
            align="center"
            prop="state"
            label="状态"
            width="80"
          ></el-table-column>
          <el-table-column align="center" fixed="right" label="操作">
            <div slot-scope="scope" v-if="scope.row.state == '已认领'">
              <el-button @click="AvailableChannel(scope.row)" type="text"
                >代付</el-button
              >
              <el-button type="text">
                |
              </el-button>
              <el-button type="text" @click="outMoney(scope.row)">
                人工出款
              </el-button>
              <el-button type="text" @click="refused(scope.row)"
                >拒绝</el-button
              >
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

        <el-dialog
          title="代付通道选择"
          :visible.sync="dialogTableVisible"
          width="40%"
        >
          <el-form
            label-width="100px"
            :rules="rules"
            ref="ruleForm"
            :model="formLabelAlign"
          >
            <el-form-item label="提现金额：">
              <el-input
                readonly
                maxlength="12"
                v-model="formLabelAlign.name"
              ></el-input>
            </el-form-item>
            <el-form-item label="银行：">
              <el-input
                readonly
                maxlength="10"
                v-model="formLabelAlign.bank"
              ></el-input>
            </el-form-item>
            <el-form-item label="通道：" prop="channel">
              <el-select v-model="formLabelAlign.channel" placeholder="请选择">
                <el-option
                  v-for="item in channelOptions"
                  :key="item.key"
                  :label="item.key"
                  :value="item.value"
                >
                </el-option>
              </el-select>
            </el-form-item>
          </el-form>
          <el-row class="formsub">
            <el-button type="primary" @click="submitForm">确定</el-button>
          </el-row>
        </el-dialog>
      </section>
    </main>
    <keep-alive v-else>
      <router-view @upData="upData"></router-view>
    </keep-alive>
  </main>
</template>

<script >
import { tradeReviewList, tradeAvailableChannel, tradeRefuseReimburse, tradeWithdrawLaunch } from '../../api/getData'


export default {
  data () {
    return {
      time: new Date(),
      dialogTableVisible: false,
      activeName: '全部', //默认显示全部
      channelOptions: null, //通道列表
      tableData: null,
      total: null,  //列表总数
      itemInif: null, //选中的订单信息
      // 代付通道选择
      formLabelAlign: {
        name: '',
        bank: '',
        channel: ''
      },
      rules: {
        channel: [
          { required: true, message: '请选择通道', trigger: 'change' }
        ]
      },
      currentPage: 1 //页数
    }
  },

  activated () {
    this.init()
  },
  methods: {
    // 初始化获取列表信息
    async init () {
      let params = {
        year: this.time.getFullYear(),  //年
        mouth: this.time.getMonth() + 1   //月
      }
      const data = await tradeReviewList(params)
      if (data) {
        this.tableData = data.data.entries
        this.total = Number(data.data.total)
      }
    },
    // 分页
    handleCurrentChange (val) {
      console.log(`当前页: ${val}`);
    },
    // 获取代付通道
    async AvailableChannel (item) {
      this.itemInif = item
      this.formLabelAlign.name = item.amount
      this.formLabelAlign.bank = item.bank_name
      let params = {
        bank_type: item.bank_type,
        merchant_name: item.merchant,
        amount: item.amount
      }
      const data = await tradeAvailableChannel(params)
      if (data) {
        this.channelOptions = data.data.entries
        this.dialogTableVisible = true
      }

    },
    // 提交代付
    async submit () {
      let params = {
        merchant: this.itemInif.merchant,
        order_id: this.itemInif.order_id,
        channel_id: this.formLabelAlign.channel
      }

      const data = await tradeWithdrawLaunch(params)
      console.warn(data)
      if (data) {
        this.itemInif.state = "处理中"
        this.dialogTableVisible = false
      }
    },
    submitForm () {
      this.$refs['ruleForm'].validate((valid) => {
        if (valid) {
          this.submit()
        } else {
          return false;
        }
      });

    },
    // 人工出款
    outMoney (item) {
      this.$router.push({ path: 'artificialOutMoney', query: { data: item } })
    },

    // 拒绝
    async refused (item) {
      this.$confirm('是否确定拒绝，该操作将商户和用户增加对应的金额。', '拒绝确认', {
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
      }
    },
    upData () {
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
    time: function () {
      this.init()
    }
  }
}
</script>

<style lang="less" scoped>
@import "../../style/mixin";
.fillcontain {
  padding: 20px;
  box-sizing: border-box;
  .formsub {
    text-align: right;
  }
  .el-select {
    width: 100%;
  }
}
</style>


