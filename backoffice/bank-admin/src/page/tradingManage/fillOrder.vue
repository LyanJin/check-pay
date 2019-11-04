<template>
  <main class="fillcontain">
    <section class="fillBody">
      <el-steps :active="active" finish-status="success">
        <el-step title="填写补单信息"></el-step>
        <el-step title="确认补单信息"></el-step>
        <el-step title="完成"></el-step>
      </el-steps>
      <!-- 填写补单信息 -->
      <fillOrderInfo
        @next="next"
        v-show="active == 0"
      ></fillOrderInfo>
      <!-- 确认补单信息 -->
      <fillOrderConfirm
        @next="next"
        @back="back"
        :fillOrder="fillOrder"
        v-show="active == 1"
      ></fillOrderConfirm>
      <!-- 完成 -->
      <fillOrderFinish
        @next="next"
        @back="back"
        :fillOrder="fillOrder"
        v-show="active == 2"
      ></fillOrderFinish>
    </section>
  </main>
</template>

<script >

import fillOrderInfo from '../../components/fillOrderInfo'
import fillOrderConfirm from '../../components/fillOrderConfirm'
import fillOrderFinish from '../../components/fillOrderFinish'

export default {
  name: 'fillOrder',
  data () {
    return {
      active: 0,
      fillOrder: 0,  //人工补单数据
    }
  },
  components: {
    fillOrderInfo,
    fillOrderConfirm,
    fillOrderFinish
  },
  activated () {
    this.active = 0
  },
  methods: {
    next (data) {
      // 更新人工补单数据
      console.warn(data)
      if (data) {
        this.fillOrder = data
      }

      if (this.active++ > 2) this.active = 0;
    },
    back (data) {
      console.log(data)
      if (data == 3) {
        this.active = 0
        return
      }

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


