<template>
  <main>
    <header-top :headTitle="title"></header-top>
    <!-- 获取验证码 -->
    <verification
      v-if="getPayPaw"
      :phone="$route.params.phone"
      @getCode="init"
    ></verification>

    <!-- 密码 -->
    <forgetPayPaw :phone="$route.params.phone" v-else></forgetPayPaw>
    <Keyboard v-if="pageType" :show="true" :length="length"></Keyboard>
  </main>
</template>

<script>
import Keyboard from '../../components/Keyboard'
import headerTop from '../../components/head'
import verification from './verification'
import forgetPayPaw from './forget-pay-paw'
import { getSessStore } from '@/config/common'
import { mapMutations } from 'vuex'
import { setTimeout } from 'timers';

export default {
  name: 'verificationCode',
  data () {
    return {
      title: null,
      pageType: null, //页面类型
      length: null,  //键盘输入值长度
      getPayPaw: null,     //是否显示验证码
    }
  },
  mounted () {
    this.init()
    // 添加事件监听页面刷新
    window.addEventListener('load', e => this.beforeunloadFn())
  },
  components: {
    Keyboard,
    headerTop,
    verification,
    forgetPayPaw
  },
  computed: {

  },
  methods: {
    ...mapMutations([
      'KEYBOARD'
    ]),
    beforeunloadFn () {
      this.$router.replace({ path: '/' })
    },
    init () {
      this.pageType = getSessStore('pageType')
      if (this.$route.params.phone) {
        this.phone = this.$route.params.phone
      }
      switch (this.pageType) {
        case 'Forget':
          this.title = '找回密码'
          this.length = 4
          this.getPayPaw = true
          break;
        case 'Registered':
          this.title = '注册'
          this.length = 4
          this.getPayPaw = true
          break;
        case 'newPay':
          this.title = '设置支付密码'
          this.length = 6
          this.getPayPaw = false
          break;
        case 'forgetPayCode':
          // 忘记支付密码检验验证码
          this.title = '找回支付密码'
          this.length = 4
          this.getPayPaw = true
          break;
        case 'forgetPay':
          // 忘记支付密码设置新密码
          this.title = '找回支付密码'
          this.length = 6
          this.getPayPaw = false
          break;
        case 'changePay':
          this.title = '修改支付密码'
          this.length = 6
          this.getPayPaw = false
          break;
      }
      if (this.pageType != 'forgetPay') {
        this.KEYBOARD('')
      }
    }
  },
  // 销毁页面时调用
  destroyed () {
    // 删除监听事件
    window.removeEventListener('load', e => this.beforeunloadFn())
  }
}
</script>

<style scoped lang="scss">
@import "src/style/mixin";

main {
  text-align: center;
  padding-top: 0.92rem;
}
</style>
