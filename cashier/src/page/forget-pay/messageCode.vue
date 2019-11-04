<template>
  <main class="main">
    <header-top headTitle="验证手机号"></header-top>
    <div class="loginForm">
      <h1>验证手机号</h1>
      <p>
        <img src="../../assets/image/phoneCode.png" alt="" />
      </p>
      <div class="text">
        为了保障您的资金安全，当期需要验证您的手机号（
        {{ hideCode(phone) }} ）
      </div>
      <button class="publicButton" @click="next">
        通过短信验证
      </button>
    </div>
  </main>
</template>

<script>
import headerTop from '../../components/head'
import { setSessStore, getSessStore } from '@/config/common'
import { forgetPassw } from '@/api/getData'

export default {
  data () {
    return {
      phone: null  //手机号
    }
  },
  activated () {
    this.phone = getSessStore('phone').phone
  },
  components: {
    headerTop
  },
  methods: {
    // 隐藏号码中间部分
    hideCode (data) {
      if (data) {
        return data.replace(/^(\d{3})\d{4}(\d+)/, "$1****$2")
      }
    },
    async next () {
      setSessStore('pageType', 'forgetPayCode')
      this.$router.push({ name: 'verificationCode', params: { phone: this.phone } })
    },
  },
  computed: {

  },
  watch: {

  }
}
</script>

<style lang="scss" scoped>
@import "src/style/mixin";

.main {
  padding: 0 0.65rem;
  padding-top: 0.92rem;
  .loginForm {
    h1 {
      padding-top: 1rem;
      padding-bottom: 0.4rem;
      text-align: center;
      font-size: 0.5rem;
    }
    img {
      width: 1.55rem;
      display: block;
      margin: 0 auto;
    }
    .text {
      padding: 0.3rem 0.6rem;
      font-size: 0.28rem;
      padding-bottom: 0.8rem;
    }
  }
}
</style>
