<template>
  <main class="main">
    <!-- 提现订单展示列表 -->
    <section class="fillcontain" v-if="tableData">
      <el-row :gutter="20">
        <el-col :span="6" class="label">提现金额：</el-col>
        <el-col :span="15" class="text" style="color: rgba(250, 84, 28, 0.6)">
          {{ tableData.amount | NumFormat }}
        </el-col>
        <el-col :span="3">
          <el-button @click="copy(tableData.amount)">
            复制
          </el-button>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="6" class="label">开户名：</el-col>
        <el-col :span="15" class="text">{{ tableData.account_name }}</el-col>
        <el-col :span="3">
          <el-button @click="copy(tableData.account_name)">
            复制
          </el-button>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="6" class="label">银行卡号：</el-col>
        <el-col :span="15" class="text">{{ tableData.card_no }}</el-col>
        <el-col :span="3">
          <el-button @click="copy(tableData.card_no)">
            复制
          </el-button>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="6" class="label">开户银行：</el-col>
        <el-col :span="15" class="text">{{ tableData.bank_name }}</el-col>
        <el-col :span="3">
          <el-button @click="copy(tableData.bank_name)">
            复制
          </el-button>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="6" class="label">省份：</el-col>
        <el-col :span="15">{{ tableData.province }}</el-col>
        <el-col :span="3">
          <el-button @click="copy(tableData.province)">
            复制
          </el-button>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="6" class="label">城市：</el-col>
        <el-col :span="15">{{ tableData.city }}</el-col>
        <el-col :span="3">
          <el-button @click="copy(tableData.city)">
            复制
          </el-button>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="6" class="label">支行：</el-col>
        <el-col :span="15">{{ tableData.branch }}</el-col>
        <el-col :span="3" v-if="tableData.branch">
          <el-button @click="copy(tableData.branch)">
            复制
          </el-button>
        </el-col>
      </el-row>
      <el-row :gutter="20" style="height: auto;">
        <el-col :span="6" class="label">备注：</el-col>
        <el-col :span="18">
          <el-input
            type="textarea"
            :autosize="{ minRows: 4, maxRows: 6 }"
            placeholder="请输入内容"
            v-model="textarea"
          >
          </el-input>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="6" class="label">转账手续费：</el-col>
        <el-col :span="18">
          <el-input
            v-model="fee"
            type="number"
            maxlength="12"
            placeholder="请输入内容"
          ></el-input>
        </el-col>
      </el-row>
      <el-row class="formsub">
        <el-button type="primary" @click="submit">
          出款完成
        </el-button>
      </el-row>
    </section>
  </main>
</template>

<script >
import { tradePersonExecute, tradePersonDone, tradeBankInfo } from '../../api/getData'

export default {
  data () {
    return {
      tableData: null,
      fee: null,  //转账手续费
      textarea: null,  //备注

    }
  },

  async activated () {
    if (this.$route.query.data.order_id) {
      let params = {
        order_id: this.$route.query.data.order_id,
        merchant: this.$route.query.data.merchant
      }
      const data = await tradeBankInfo(params)
      if (data) {
        this.tableData = data.data.bank_entry
      }
    } else {
      this.$router.go(-1)
    }

  },
  methods: {
    // 出款完成
    async submit () {
      if (!this.textarea) {
        this.$message({
          showClose: true,
          message: '备注不能为空！',
          type: 'error'
        });
        return
      }
      if (!this.fee) {
        this.$message({
          showClose: true,
          message: '转账手续费不能为空！',
          type: 'error'
        });
        return
      }
      if (this.fee < 0) {
        this.$message({
          showClose: true,
          message: '转账手续费不能为负数！',
          type: 'error'
        });
        return
      }
      let res = null
      if (this.$route.query.data.state == '处理中') {
        let params = {
          order_id: this.$route.query.data.order_id,
          merchant: this.$route.query.data.merchant,
          comment: this.textarea,
          fee: this.fee
        }
        res = await tradePersonDone(params)

      } else {
        let params = {
          order_id: this.$route.query.data.order_id,
          merchant: this.$route.query.data.merchant
        }
        const data = await tradePersonExecute(params)
        if (data) {
          params = {
            order_id: this.$route.query.data.order_id,
            merchant: this.$route.query.data.merchant,
            comment: this.textarea,
            fee: this.fee
          }
          res = await tradePersonDone(params)
        }
      }
      // 出款完成返回上一页
      if (res) {
        this.$emit("upData")
        this.$message({
          message: '提交成功',
          type: 'success'
        });
        setTimeout(() => {
          this.$router.go(-1)
        }, 1000)
      }

    },
    // 点击复制
    copy (data) {
      console.warn(data)
      let textArea = document.createElement("textarea");
      textArea.style.position = 'fixed';
      textArea.style.top = '0';
      textArea.style.left = '0';
      textArea.style.width = '2px';
      textArea.style.height = '2px';
      textArea.value = data;
      document.body.appendChild(textArea);
      textArea.select();
      try {
        let successful = document.execCommand('copy');
        if (successful) {
          this.$message({
            message: '复制成功',
            type: 'success'
          });
        } else {
          this.$message({
            message: '该浏览器不支持点击复制',
            type: 'error'
          });
        }
      } catch (err) {
        this.$message({
          message: '该浏览器不支持点击复制',
          type: 'error'
        });
      }
      document.body.removeChild(textArea);
    }
  },

}
</script>

<style lang="less" scoped>
@import "../../style/mixin";
.main {
  padding: 20px;
  .fillcontain {
    width: 700px;
    margin: auto;
    .el-row {
      height: 60px;
      line-height: 60px;
      .label {
        text-align: right;
      }
      .text {
        font-size: 30px;
      }
    }
    .formsub {
      text-align: center;
    }
  }
}
</style>


