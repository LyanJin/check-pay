<template>
  <main>
    <div class="text">我们已给您的</br>手机号{{ hideCode(phone) }}发送验证码</div>
    <div class="code-input-main">
      <span
        class="code-input-main-item border-1"
        for="code"
        v-for="(value, index) in length"
        :key="value"
      >
        {{ keyboard[index] }}
      </span>
    </div>
    <div class="code">
      <span class="code-time" v-show="computedTime > 0"
        >{{ computedTime }}秒后重新发送</span
      >
      <span v-show="computedTime == 0" @click="getVerifyCode">重新发送</span>
    </div>
  </main>
</template>

<script>
import { smsVerify, smsGet, forgetVerify, forgetPassw } from '@/api/getData';
import { mapState } from 'vuex'
import { constants } from 'fs';
import { getSessStore, setSessStore } from '@/config/common'

export default {
  props: {
    phone: null,
  },
  data () {
    return {
      length: 4,    //验证码位数
      computedTime: -1,   // 验证码倒计时
      pageType: null   // 页面类型
    }
  },

  created () {
    this.pageType = getSessStore('pageType')
    if (this.pageType == 'Registered' || this.pageType == 'forgetPayCode') {
      this.getVerifyCode()   //进入自动获取验证码
    }
    if (this.pageType == 'Forget') {
      this.CodeNumber()      //进入倒计时
    }
  },
  methods: {
    // 获取验证码
    async getVerifyCode () {
      // 获取验证码
      if (this.computedTime <= 0) {
        switch (this.pageType) {
          // 注册初始化密码
          case 'Registered':
            if (this.phone) {
              let code = await smsGet({ "number": this.areaCode.phone_code + this.phone });
            } else {
              this.$toast('未获取到手机号');
              setTimeout(() => {
                this.$router.replace({ path: '/' })
              }, 1000)
            }
            break;
          // 忘记支付密码
          case 'forgetPayCode':
            if (this.phone) {
              let data = await forgetPassw({ "number": getSessStore('phone').area + this.phone });
            } else {
              this.$toast('未获取到手机号');
              setTimeout(() => {
                this.$router.replace({ path: '/' })
              }, 1000)
            }
            break;
          // 忘记密码
          case 'Forget':
            if (this.phone) {
              let data = await forgetPassw({ "number": this.areaCode.phone_code + this.phone });
            } else {
              this.$toast('未获取到手机号');
              setTimeout(() => {
                this.$router.replace({ path: '/' })
              }, 1000)
            }
            break;
        }
        this.CodeNumber()
      }
    },
    // 倒计时
    CodeNumber () {
      console.warn(this.computedTime)
      if (this.computedTime <= 0) {
        this.computedTime = 60
        // console.warn(this.computedTime)
        clearInterval(this.timer)
        this.timer = setInterval(() => {
          this.computedTime--;
          // console.warn(this.computedTime)
          if (this.computedTime == 0) {
            clearInterval(this.timer)
          }
        }, 1000)
      }
    },
    // 隐藏号码中间部分
    hideCode (data) {
      if (data) {
        return data.replace(/^(\d{3})\d{4}(\d+)/, "$1****$2")
      }
    },
    async next () {
      let params = {
        "number": this.areaCode.phone_code + this.phone,
        "auth_code": this.keyboard
      }, data
      // 自动校验验证码是否正确
      if (this.pageType == 'Registered') {
        // 注册验证码
        data = await smsVerify(params)
      } else if (this.pageType == 'Forget' || this.pageType == 'forgetPayCode') {
        // 找回密码验证码
        if (getSessStore('phone') && getSessStore('phone').area) {
          params.number = getSessStore('phone').area + getSessStore('phone').phone // 获取当前用户号码
        }
        data = await forgetVerify(params)
      }
      if (data) {
        // 成功设置密码
        if (this.pageType == 'Registered') {
          setSessStore("pageType", "Password")
        } else if (this.pageType == 'Forget') {
          setSessStore("pageType", "ForgetPassword")
        }
        if (this.pageType == 'forgetPayCode') {
          setSessStore('pageType', 'forgetPay')
          this.$emit('getCode')
        } else {
          this.$router.replace({ name: 'forget', params: { code: this.keyboard, phone: this.phone } })
        }
      }
    }
  },
  computed: {
    ...mapState([
      'areaCode', 'keyboard'
    ])
  },
  watch: {
    keyboard: function () {
      if (this.keyboard.length >= 4) {
        this.next()
      }
    }
  },

}
</script>

<style scoped lang="scss">
@import "src/style/mixin";

main {
  .text {
    font-size: 0.34rem;
    margin-top: 1rem;
    margin-bottom: 0.6rem;
  }
  .code {
    font-size: 0.28rem;
    margin-top: 0.2rem;
    .code-time {
      color: #999;
    }
    span {
      color: #609fff;
      overflow: hidden;
    }
  }
  .code-input-main-item {
    @include wh(0.9rem, 0.9rem);
    line-height: 0.9rem;
    margin-right: 0.2rem;
    font-size: 0.5rem;
    display: inline-block;
    vertical-align: middle;
  }
}
</style>
