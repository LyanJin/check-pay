<template>
  <main class="fillcontain">
    <!-- 商户余额调整 -->
    <el-form label-width="100px" v-if="balanceEdit">
      <el-form-item label="商户">
        {{ balanceEdit.name }}
      </el-form-item>

      <el-form-item label="调整类型">
        <el-radio v-model="adjustment_type" label="PLUS">调整增加</el-radio>
        <el-radio v-model="adjustment_type" label="MINUS">调整扣除</el-radio>
        <el-radio v-model="adjustment_type" label="FROZEN">资金冻结</el-radio>
        <el-radio v-model="adjustment_type" label="UNFROZEN">资金解冻</el-radio>
        <el-radio v-model="adjustment_type" label="MINUS_INCOME"
          >在途资金扣减</el-radio
        >
      </el-form-item>
      <el-form-item label="调整金额">
        <el-input
          v-model="amount"
          @input="amount = amount.replace(/^(0+)|[^\d.]/g, '')"
          clearable
          maxlength="12"
        ></el-input>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="onSubmit">下一步</el-button>
      </el-form-item>
    </el-form>

    <!-- 人工补单列表 -->
    <el-form
      ref="orderForm"
      :model="orderForm"
      :rules="orderFormRules"
      label-width="100px"
      v-else-if="orderConfig"
    >
      <el-form-item label="用户ID" prop="uid">
        <el-input v-model="orderForm.uid" maxlength="30" clearable></el-input>
      </el-form-item>
      <el-form-item label="商户" prop="merchant">
        <el-select v-model="orderForm.merchant" clearable placeholder="请选择">
          <el-option
            v-for="item in orderConfig.merchant"
            :key="item.value"
            :label="item.desc"
            :value="item.desc"
          >
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="支付方式" prop="payment_type">
        <el-select
          v-model="orderForm.payment_type"
          clearable
          placeholder="请选择支付方式"
        >
          <el-option
            v-for="item in orderConfig.payment_type"
            :key="item.value"
            :label="item.desc"
            :value="item.value"
          >
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="通道" prop="channel_id">
        <el-select
          v-model="orderForm.channel_id"
          clearable
          placeholder="请选择支付类型"
        >
          <el-option
            v-for="item in orderConfig.deposit_channel"
            :key="item.value"
            :label="item.desc"
            :value="item.value"
          >
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="通道订单号" prop="mch_tx_id">
        <el-input
          v-model="orderForm.mch_tx_id"
          maxlength="40"
          clearable
        ></el-input>
      </el-form-item>
      <el-form-item label="金额" prop="amount">
        <el-input
          v-model="orderForm.amount"
          maxlength="12"
          clearable
        ></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="orderSubmit('orderForm')"
          >下一步</el-button
        >
      </el-form-item>
    </el-form>

    <!-- 用户余额调整 -->
    <el-form label-width="100px" v-else-if="userBalanceEdit">
      <el-form-item label="用户ID">
        {{ userBalanceEdit.user_id }}
      </el-form-item>

      <el-form-item label="调整类型">
        <el-radio v-model="adjustment_type" label="1">调整增加</el-radio>
        <el-radio v-model="adjustment_type" label="2">调整扣除</el-radio>
      </el-form-item>
      <el-form-item label="调整金额">
        <el-input
          v-model="amount"
          @input="amount = amount.replace(/^(0+)|[^\d.]/g, '')"
          clearable
          maxlength="12"
        ></el-input>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="onUserSubmit">下一步</el-button>
      </el-form-item>
    </el-form>
  </main>
</template>

<script>

import { depositConfigGet } from '@/api/getData'

export default {
  props: {
    balanceEdit: null,  //商户余额调整
    userBalanceEdit: null //用户余额调整
  },
  data () {
    return {
      adjustment_type: '',  //调整类型
      amount: '', //调整金额

      /**
       * 
       *  充值订单查询人工补单数据
       * 
       */
      orderForm: {
        uid: null,
        merchant: null,
        amount: null,
        channel_id: null,
        mch_tx_id: null,
        payment_type: null,
      },
      orderFormRules: {
        merchant: [
          { required: true, message: '请选择商户', trigger: 'change' }
        ],
        payment_type: [
          { required: true, message: '请选择支付方式', trigger: 'change' }
        ],
        channel_id: [
          { required: true, message: '请选择通道', trigger: 'change' }
        ],
        mch_tx_id: [
          { required: true, message: '请输入通道订单号', trigger: 'change' }
        ],
        amount: [
          { required: true, message: '请输入金额', trigger: 'change' }
        ],
      },
      orderConfig: null  //系统配置信息

    }
  },

  async created () {
    // 获取人工补单配置
    if (!this.balanceEdit && !this.userBalanceEdit) {
      const data = await depositConfigGet()
      if (data) {
        this.orderConfig = data.data
      }
      console.warn(this.orderConfig)
    }
  },
  methods: {
    // 商户余额调整
    onSubmit () {
      if (!this.adjustment_type) {
        this.$message.error('请选择类型');
        return
      }
      if (!this.amount) {
        this.$message.error('请输入金额');
        return
      }
      this.balanceEdit.amount = this.amount
      this.balanceEdit.adjustment_type = this.adjustment_type
      this.$emit('next', this.balanceEdit)
    },

    // 充值详情人工补单下一步
    orderSubmit (formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          this.$emit('next', this.orderForm)
        } else {
          console.log('error submit!!');
          return false;
        }
      });
    },

    // 用户余额调整
    onUserSubmit () {
      if (!this.adjustment_type) {
        this.$message.error('请选择类型');
        return
      }
      if (!this.amount) {
        this.$message.error('请输入金额');
        return
      }
      this.userBalanceEdit.amount = this.amount
      this.userBalanceEdit.adjust_type = this.adjustment_type
      this.$emit('next', this.userBalanceEdit)
    },
  },
  watch: {


  }
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
}
</style>


