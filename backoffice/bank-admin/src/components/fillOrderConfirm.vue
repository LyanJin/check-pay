<template>
  <main class="fillcontain">
    <section v-if="balanceEdit">
      <el-alert
        effect="dark"
        title="确认后，将直接调整商户余额，无法退回。"
        type="warning"
        center
        show-icon
      >
      </el-alert>

      <!-- 商户余额调整 -->
      <el-form label-width="100px">
        <el-form-item label="商户：">
          {{ balanceEdit.name }}
        </el-form-item>

        <el-form-item label="调整类型：">
          <span v-if="balanceEdit.adjustment_type == 'PLUS'">
            调整增加
          </span>
          <span v-if="balanceEdit.adjustment_type == 'MINUS'">
            调整扣除
          </span>
          <span v-if="balanceEdit.adjustment_type == 'FROZEN'">
            资金冻结
          </span>
          <span v-if="balanceEdit.adjustment_type == 'UNFROZEN'">
            资金解冻
          </span>
          <span v-if="balanceEdit.adjustment_type == 'MINUS_INCOME'">
            在途资金扣除
          </span>
        </el-form-item>

        <el-form-item label="调整金额：">
          <span class="moneytyle">
            <em v-if="balanceEdit.adjustment_type == 'PLUS'">+</em>
            <em
              v-if="
                balanceEdit.adjustment_type == 'MINUS' ||
                  balanceEdit.adjustment_type == 'MINUS_INCOME'
              "
              >-</em
            >
            {{ balanceEdit.amount | NumFormat }}
          </span>
        </el-form-item>

        <el-form-item label="说明原因：">
          <el-input
            type="textarea"
            placeholder="请输入原因"
            v-model="balanceEdit.reason"
            maxlength="500"
            show-word-limit
            :rows="4"
          >
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onSubmit">提交</el-button>
          <el-button @click="back">返回修改 </el-button>
        </el-form-item>
      </el-form>
    </section>

    <!-- 人工补单列表 -->
    <section v-if="fillOrder">
      <el-alert
        effect="dark"
        title="确认补单后，将直接为用户以及商户添加金额，无法退回。"
        type="warning"
        center
        show-icon
      >
      </el-alert>
      <el-form label-width="100px">
        <el-form-item label="用户ID：">
          {{ fillOrder.uid }}
        </el-form-item>
        <el-form-item label="商户：">
          {{ fillOrder.merchant }}
        </el-form-item>
        <el-form-item label="支付方式：">
          {{ fillOrder.payment_type }}
        </el-form-item>
        <el-form-item label="通道：">
          {{ fillOrder.channel_id }}
        </el-form-item>
        <el-form-item label="通道订单号：">
          {{ fillOrder.mch_tx_id }}
        </el-form-item>
        <el-form-item label="金额：">
          <span class="moneytyle">
            {{ fillOrder.amount | NumFormat }}
          </span>
        </el-form-item>
        <el-form-item label="说明原因：">
          <el-input
            type="textarea"
            placeholder="请输入原因"
            v-model="fillOrder.remark"
            maxlength="500"
            show-word-limit
            :rows="4"
          >
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="orderSubmit">提交</el-button>
          <el-button @click="back">返回修改 </el-button>
        </el-form-item>
      </el-form>
    </section>

    <section v-if="userBalanceEdit">
      <el-alert
        effect="dark"
        title="确认后，将直接调整用户余额，无法退回。"
        type="warning"
        center
        show-icon
      >
      </el-alert>

      <!-- 用户余额调整 -->
      <el-form label-width="100px">
        <el-form-item label="用户ID：">
          {{ userBalanceEdit.user_id }}
        </el-form-item>

        <el-form-item label="调整类型：">
          <span v-if="userBalanceEdit.adjust_type == '1'">
            调整增加
          </span>
          <span v-if="userBalanceEdit.adjust_type == '2'">
            调整扣除
          </span>
        </el-form-item>

        <el-form-item label="调整金额：">
          <span class="moneytyle">
            <em v-if="userBalanceEdit.adjust_type == '1'">+</em>
            <em v-if="userBalanceEdit.adjust_type == '2'">-</em>
            {{ userBalanceEdit.amount | NumFormat }}
          </span>
        </el-form-item>

        <el-form-item label="说明原因：">
          <el-input
            type="textarea"
            placeholder="请输入原因"
            v-model="userBalanceEdit.reason"
            maxlength="500"
            show-word-limit
            :rows="4"
          >
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onUserSubmit">提交</el-button>
          <el-button @click="back">返回修改 </el-button>
        </el-form-item>
      </el-form>
    </section>
  </main>
</template>

<script>
import { balanceEdit, tradeOrderCreate, userManageBalanceEdit } from '@/api/getData'

export default {
  props: {
    fillOrder: null,     //人工补单
    balanceEdit: null,//商户余额调整数据
    userBalanceEdit: null //用户余额调整
  },
  data () {
    return {
      textarea: null  //备注
    }
  },
  methods: {
    // 提交商户余额调整
    async onSubmit () {
      if (!this.balanceEdit.reason) {
        this.$message.error('请输入原因');
        return
      }
      let params = {
        name: this.balanceEdit.name,
        adjustment_type: this.balanceEdit.adjustment_type,
        amount: this.balanceEdit.amount,
        reason: this.balanceEdit.reason
      }
      console.warn(params)
      const res = await balanceEdit(params)
      if (res) {
        this.$emit('next', this.balanceEdit)
      }
    },

    // 充值详情人工补单提交
    async orderSubmit () {
      if (!this.fillOrder.remark) {
        this.$message.error('请输入原因');
        return
      }
      const res = await tradeOrderCreate(this.fillOrder)
      if (res) {
        this.$emit('next', this.fillOrder)
      }
    },

    // 提交用户余额调整
    async onUserSubmit () {
      if (!this.userBalanceEdit.reason) {
        this.$message.error('请输入原因');
        return
      }
      let params = {
        uid: this.userBalanceEdit.user_id,
        adjust_type: this.userBalanceEdit.adjust_type,
        amount: this.userBalanceEdit.amount,
        comment: this.userBalanceEdit.reason
      }
      console.warn(params)
      const res = await userManageBalanceEdit(params)
      if (res) {
        this.$emit('next', this.userBalanceEdit)
      }
    },

    back () {
      this.$emit('back')
    }
  },
}
</script>

<style lang="less" scoped>
@import "../style/mixin";
.fillcontain {
  padding: 20px 240px;
  box-sizing: border-box;
  .el-select {
    width: 100%;
  }
  .moneytyle {
    line-height: 30px;
    font-size: 24px;
    color: #e6a23c;
    em {
      vertical-align: top;
    }
  }
}
</style>


