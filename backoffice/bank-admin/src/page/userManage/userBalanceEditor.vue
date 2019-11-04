<template>
  <main class="fillcontain">
    <section class="fillBody">
      <el-steps :active="active" finish-status="success">
        <el-step title="填写调整信息"></el-step>
        <el-step title="确认调整信息"></el-step>
        <el-step title="完成"></el-step>
      </el-steps>
      <!-- 填写补单信息 -->
      <fillOrderInfo
        @next="next"
        v-show="active == 0"
        :userBalanceEdit="userBalanceEdit"
      ></fillOrderInfo>
      <!-- 确认补单信息 -->
      <fillOrderConfirm
        :userBalanceEdit="userBalanceEdit"
        @next="next"
        @back="back"
        v-show="active == 1"
      ></fillOrderConfirm>
      <!-- 完成 -->
      <fillOrderFinish
        :userBalanceEdit="userBalanceEdit"
        @next="next"
        @back="back"
        v-show="active == 2"
      ></fillOrderFinish>
    </section>
  </main>
</template>

<script >

import fillOrderInfo from '@/components/fillOrderInfo'
import fillOrderConfirm from '@/components/fillOrderConfirm'
import fillOrderFinish from '@/components/fillOrderFinish'
import { getSessStore } from '@/config/mUtils'

export default {
  name: 'userBalanceEditor',
  data () {
    return {
      active: 0,
      userBalanceEdit: null  //商户余额调整数据
    }
  },
  components: {
    fillOrderInfo,
    fillOrderConfirm,
    fillOrderFinish
  },
  created () {
    this.active = 0
    this.userBalanceEdit = getSessStore('USER_BALANCE_EDIT')
  },
  methods: {
    next (data) {
      // 更新用户余额调整
      console.warn(data)
      if (data) {
        this.userBalanceEdit = data
      }

      if (this.active++ > 2) this.active = 0;
    },
    back () {
      if (this.active-- < 0) this.active = 0;
    }
  },
}
</script>

<style lang="less" scoped>
@import "../../style/mixin";
.fillBody {
  padding: 20px;
  .el-steps {
    padding: 0 120px;
  }
}
</style>
