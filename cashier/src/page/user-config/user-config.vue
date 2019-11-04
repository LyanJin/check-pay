<template>
  <div>
    <div class="main">
      <ul class="config-list">
        <li class="border-bottom">修改登录密码</li>
        <li class="border-bottom">修改支付密码</li>
        <li class="border-bottom">忘记支付密码</li>
      </ul>
    </div>
    <div class="footer">
      <button class="exit">退出登录</button>
    </div>
  </div>
</template>

<script>
import loading from '../../components/loading'

export default {
  data () {
    return {
      phoneNumber: null, // 手机号
      passWord: null, // 密码
      showPassword: false, // 是否显示密码
      showLoading: false,
      keyboard: false
    }
  },
  components: {
    loading
  },
  methods: {
    // 是否显示密码
    changePassWordType () {
      this.showPassword = !this.showPassword
    },
    userDelete () {
      this.phoneNumber = ''
    },
    Login () {
      this.showLoading = true

      setTimeout(() => {
        this.showLoading = false
      }, 3000)
    },
    // 调用自定义键盘
    input () {
      this.keyboard = true
    },
    typing (data) {
      this.phoneNumber = data
      console.warn('typing' + data)
    },
    blur (data) {
      console.warn('blur' + data)
    }
  }
}
</script>

<style scoped lang="scss">
@import "../../style/mixin";
.main {
  .config-list {
    width: 100%;
    li {
      @include wh(100%, 1rem);
      display: inline-block;
      background: #fff;
      border: none;
    }
  }
}
.footer {
  position: absolute;
  bottom: 0;
  @include wh(100%, 1rem);
  .exit {
  }
}
</style>
