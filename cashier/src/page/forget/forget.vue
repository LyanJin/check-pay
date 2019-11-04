<template>
  <main class="main">
    <header-top :headTitle="title"></header-top>

    <!-- 输入手机号 -->
    <registered v-if="isphone" :type="type"></registered>

    <!-- 验证成功设置新密码 -->
    <newPass
      v-else
      :text="text"
      :old="old"
      :phone="this.$route.params.phone"
      :code="this.$route.params.code"
      @changeOld="changeOld"
    ></newPass>
  </main>
</template>

<script>
import headerTop from '../../components/head'
import registered from './registered';
import newPass from './new-pass';
import { mapState } from 'vuex'
import { getSessStore } from '@/config/common'

export default {
  name: 'forget',
  data () {
    return {
      title: null, // 标题
      text: null,  // 提示语
      isphone: true,
      old: false,
      type: null
    }
  },
  created () {
    this.type = getSessStore('pageType')
    console.warn(this.type)
    console.warn(this.old)
    this.init(this.type)
  },
  mounted () {
    // 添加事件监听页面刷新
    window.addEventListener('load', e => this.beforeunloadFn())
  },
  components: {
    headerTop,
    registered,
    newPass
  },
  computed: {

  },

  methods: {
    beforeunloadFn () {
      this.$router.replace('/')
    },
    // 初始化页面
    async init (data) {
      switch (data) {
        case 'Registered':  //注册账户
          this.title = '注册'
          this.isphone = true
          break;
        case 'Password':
          this.isphone = false  //注册账户设置密码
          this.old = false
          if (this.$route.params.phone) {
            this.text = '请为您的账号' + this.$route.params.phone + '</br>设置登录密码'
          }
          break;
        case 'Forget':  //找回密码
          this.title = '找回密码'
          this.old = false
          this.isphone = true
          break;
        case 'ForgetPassword':
          this.isphone = false  //找回密码设置密码
          if (this.$route.params.phone) {
            this.text = '请为您的账号' + this.$route.params.phone + '</br>设置一个新密码'
          }
          break;
        case 'ChangePassword':  //修该密码
          this.isphone = false
          this.old = true
          this.title = '修改登录密码'
          this.text = '请输入当前密码'
          break;
      }
    },
    async changeOld () {
      this.old = !this.old
    }

  },
  watch: {
  },
  // 页面销毁时调用
  destroyed () {
    // 删除监听事件
    window.removeEventListener('load', e => this.beforeunloadFn())
  }
}
</script>

<style lang="scss" scoped>
.main {
  padding-top: 0.92rem;
}
</style>
