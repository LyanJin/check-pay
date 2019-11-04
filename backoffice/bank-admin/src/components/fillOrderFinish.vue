<template>
  <main class="fillcontain">
    <h2>
      <i class="el-icon-success"></i> <br />
      操作成功
    </h2>
    <!-- 商户余额调整 -->
    <el-form label-width="100px" v-if="balanceEdit">
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
          {{ balanceEdit.amount | NumFormat }}
        </span>
      </el-form-item>
      <el-form-item>
        <el-button @click="back">返回</el-button>
      </el-form-item>
    </el-form>

    <!-- 人工补单列表 -->
    <el-form label-width="100px" v-else-if="fillOrder">
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
          {{ fillOrder.amount }}
        </span>
      </el-form-item>
      <el-form-item>
        <el-button @click="back">完成</el-button>
      </el-form-item>
    </el-form>

    <!-- 用户余额调整 -->
    <el-form label-width="100px" v-else-if="userBalanceEdit">
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
          {{ userBalanceEdit.amount | NumFormat }}
        </span>
      </el-form-item>
      <el-form-item>
        <el-button @click="userBack">返回</el-button>
      </el-form-item>
    </el-form>
  </main>
</template>

<script>

export default {
  props: {
    fillOrder: null,   //人工补单
    balanceEdit: null, //商户余额调整数据
    userBalanceEdit: null //用户余额调整
  },
  data () {
    return {

    }
  },
  methods: {
    back () {
      this.$router.push({ path: 'merchantlist' })
    },
    userBack () {
      this.$router.push({ path: 'userList' })
    }
  },
}
</script>

<style lang="less" scoped>
@import "../style/mixin";
.fillcontain {
  padding: 20px 240px;
  box-sizing: border-box;
  .el-icon-success {
    color: #67c23a;
    font-size: 70px;
  }
  h2 {
    text-align: center;
  }
  .el-select {
    width: 100%;
  }
  .moneytyle {
    font-size: 24px;
    color: #e6a23c;
  }
}
</style>


