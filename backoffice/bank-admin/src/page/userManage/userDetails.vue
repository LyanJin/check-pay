<template>
  <main class="fillcontain" v-if="userData">
    <section class="orderTime">
      <h3>
        <i class="el-icon-s-order"></i> 用户ID：
        {{ userData.headInfo.uid }}
      </h3>
      <ul class="table-state">
        <li>
          类型：<em>{{ userData.headInfo.type }}</em>
        </li>
        <li>
          来源：<em>{{ userData.headInfo.source }}</em>
        </li>
        <li>
          手机号：<em>{{ userData.headInfo.account }}</em>
        </li>
        <li>
          注册时间：<em>{{ userData.headInfo.create_time }}</em>
        </li>
      </ul>
      <div class="state-money">
        <div>
          <p>状态</p>
          <h3>
            {{ userData.headInfo.state == "ACTIVE" ? "正常" : "禁止提现" }}
          </h3>
        </div>
        <div>
          <p>余额</p>
          <h3>{{ userData.headInfo.ava_bl | NumFormat }}</h3>
        </div>
      </div>
    </section>

    <!-- 订单信息 -->
    <section class="orderInfo">
      <div>
        <h3>银行卡信息</h3>
        <div class="banklist">
          <el-table
            :data="userData.bankcardEntries"
            :header-cell-style="{ background: '#f8f8f8' }"
          >
            <el-table-column align="center" prop="bank_name" label="银行">
            </el-table-column>

            <el-table-column align="center" prop="account_name" label="持卡人">
            </el-table-column>

            <el-table-column align="center" prop="card_no" label="银行卡">
            </el-table-column>

            <el-table-column align="center" prop="province" label="开户地区">
            </el-table-column>

            <el-table-column align="center" prop="branch" label="开户支行名称">
            </el-table-column>

            <el-table-column align="center" label="操作">
              <div slot-scope="scope" style="position: relative;">
                <el-popover
                  placement="top"
                  width="160"
                  v-model="visible[scope.$index]"
                >
                  <p>确定删除这张银行卡吗？</p>
                  <div style="text-align: right; margin: 0">
                    <el-button size="mini" @click="cancel(scope.$index)">
                      取消
                    </el-button>
                    <el-button
                      size="mini"
                      type="primary"
                      @click="Delete(scope.row, scope.$index)"
                    >
                      确定
                    </el-button>
                  </div>
                  <el-button slot="reference">删除</el-button>
                </el-popover>
              </div>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </section>

    <section class="orderInfo" style=" padding: 40px 20px;">
      <el-radio-group v-model="activeName" size="medium">
        <el-radio-button label="1">充值记录</el-radio-button>
        <el-radio-button label="2">提现记录</el-radio-button>
      </el-radio-group>

      <el-table
        v-show="userDetsilForm.pay_type == 1"
        :data="tableData.entries"
        :header-row-style="{
          color: '#333'
        }"
      >
        <el-table-column align="center" prop="mch_tx_id" label="商户订单号">
        </el-table-column>

        <el-table-column align="center" prop="sys_tx_id" label="系统订单号">
        </el-table-column>

        <el-table-column align="center" prop="pay_method" label="支付方式">
        </el-table-column>

        <el-table-column align="center" label="发起金额">
          <div slot-scope="scope">
            {{ scope.row.amount | NumFormat }}
          </div>
        </el-table-column>

        <el-table-column align="center" label="实际支付金额" width="110">
          <div slot-scope="scope">
            {{ scope.row.tx_amount | NumFormat }}
          </div>
        </el-table-column>

        <el-table-column
          align="center"
          prop="create_time"
          sortable
          label="创建时间"
          width="165"
        >
        </el-table-column>

        <el-table-column
          align="center"
          prop="state"
          label="订单状态"
          width="80"
        >
        </el-table-column>
      </el-table>
      <el-table
        v-show="userDetsilForm.pay_type == 2"
        :data="tableData.entries"
        :header-row-style="{
          color: '#333'
        }"
      >
        <el-table-column align="center" prop="mch_tx_id" label="商户订单号">
        </el-table-column>

        <el-table-column align="center" prop="sys_tx_id" label="系统订单号">
        </el-table-column>

        <el-table-column align="center" prop="bank_name" label="银行">
        </el-table-column>

        <el-table-column align="center" label="银行卡号">
          <div slot-scope="scope">
            {{ scope.row.card_no }}
          </div>
        </el-table-column>

        <el-table-column align="center" label="提现金额">
          <div slot-scope="scope">
            {{ scope.row.amount | NumFormat }}
          </div>
        </el-table-column>

        <el-table-column align="center" label="手续费">
          <div slot-scope="scope">
            {{ scope.row.fee | NumFormat }}
          </div>
        </el-table-column>

        <el-table-column
          align="center"
          prop="create_time"
          sortable
          label="创建时间"
          width="165"
        >
        </el-table-column>

        <el-table-column
          align="center"
          prop="done_time"
          sortable
          label="完成时间"
          width="165"
        >
        </el-table-column>

        <el-table-column
          align="center"
          prop="state"
          label="订单状态"
          width="80"
        >
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        @current-change="handleCurrentChange"
        :current-page="userDetsilForm.page_index"
        :page-size="10"
        layout="total, prev, pager, next, jumper"
        :total="total"
        style="margin-top: 20px;text-align: center;"
      >
      </el-pagination>
    </section>
  </main>
</template>

<script >
import { userManageUserDetail, userManageBankDelete, userManageUserTransaction } from '../../api/getData'

export default {
  data () {
    return {
      userData: null,   //用户详情
      tableData: {},   //用户交易记录
      visible: [],   //删除二次确认
      userDetsilForm: {
        uid: this.$route.params.userInfo ? this.$route.params.userInfo.user_id : '',
        pay_type: '1',
        page_size: 10,
        page_index: 1
      },
      total: null,    //列表总数
      activeName: '1',    //列表总数
    }
  },

  activated () {
    if (this.$route.params.userInfo) {
      this.init()
    } else {
      this.$router.go(-1)
    }
  },
  methods: {
    // 初始化列表
    async init () {
      // 用户详情
      let data = await userManageUserDetail({ uid: this.$route.params.userInfo.user_id })
      if (data) {
        this.userData = data.data
      }

      // 用户交易记录
      this.userDetsilForm.pay_type = this.activeName
      let list = await userManageUserTransaction(this.userDetsilForm)
      if (list) {
        if (this.userDetsilForm.pay_type == 1) {
          this.tableData = list.data.depositInfo
        } else {
          this.tableData = list.data.withdrawInfo
        }
        this.total = Number(this.tableData.total)
        console.warn(this.tableData)
      }
    },
    // 删除用户银行卡
    async Delete (item, index) {
      let data = await userManageBankDelete({ card_id: item.bank_id })
      if (data) {
        console.warn(data.data)
        this.userData.bankcardEntries.splice(index, 1)
        this.visible = false
      }
    },
    // 分页
    handleCurrentChange (val) {
      this.userDetsilForm.page_index = val
      this.init()
    },
    cancel (index) {
      this.$set(this.visible, index, false);
    }
  },
  watch: {
    activeName: function () {
      this.userDetsilForm.page_index = 1
      this.init()
    },
  }
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
        width: 45%;
        line-height: 24px;
        em {
          color: #666;
          word-wrap: break-word;
        }
      }
    }
    .state-money {
      display: inline-block;
      width: 20%;
      div {
        display: inline-block;
        width: 48%;
      }
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
    .banklist {
      padding: 20px;
    }
  }
}
</style>


