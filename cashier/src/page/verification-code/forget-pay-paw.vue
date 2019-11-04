<template>
  <main>
    <div class="text">{{ text }}</div>
    <div class="code-input-main">
      <span
        class="code-input-main-item border-1"
        for="code"
        v-for="(value, index) in length"
        :key="value"
      >
        <i v-if="keyboard[index]"></i>
      </span>
    </div>

    <button
      class="publicButton"
      @click="submit"
      :class="{ isdisabled: isdisabled }"
      :disabled="isdisabled"
      v-if="showBtn"
    >
      保存新密码
    </button>
  </main>
</template>

<script>
import { mapState, mapMutations } from 'vuex'
import { getSessStore } from '@/config/common'
import { newPaymentPassword, PaymentPasswordCheck, PaymentPasswordReset, PaymentPasswordForgetSet } from '@/api/getData'
import { setTimeout } from 'timers';
import md5 from 'js-md5';

export default {
  props: {
    title: null
  },
  data () {
    return {
      showBtn: false,  //是否显示按钮
      text: null,  //提示语
      next: 0,  //流程进度
      length: 6,    //密码位数
      isdisabled: true, // 是否禁用输入账号按钮
      password: null, // 支付密码
      oldPassword: null, // 旧支付密码
      verificationCode: null, // 保存验证码
    }
  },
  async created () {
    this.next = 0
    this.showBtn = false
    this.isdisabled = true
    switch (getSessStore('pageType')) {
      case 'newPay':
        this.text = '输入支付密码'
        break;
      case 'forgetPay':
        this.text = '请设置新支付密码，用于支付验证'
        this.verificationCode = this.keyboard
        this.KEYBOARD('')
        break;
      case 'changePay':
        this.text = '请输入支付密码，以验证身份'
        break;
    }
  },
  methods: {
    ...mapMutations([
      'KEYBOARD'
    ]),
    async submit () {
      let params = {}, res
      switch (getSessStore('pageType')) {
        // 初始化支付密码
        case 'newPay':
          params = {
            payment_password: md5(this.keyboard)
          }
          res = await newPaymentPassword(params)
          if (res) {
            this.$toast.success('设置成功');
            setTimeout(() => {
              this.$router.go(-1)
            }, 1000)
          }
          break;
        // 忘记支付密码
        case 'forgetPay':
          params = {
            number: getSessStore('phone').area + getSessStore('phone').phone,
            auth_code: this.verificationCode,
            new_payment_password: md5(this.keyboard)
          }
          res = await PaymentPasswordForgetSet(params)
          if (res) {
            this.$toast.success('设置成功');
            setTimeout(() => {
              this.$router.go(-2)
            }, 1000)
          }
          break;
        // 修改支付密码
        case 'changePay':
          params = {
            ori_payment_password: this.oldPassword,
            new_payment_password: md5(this.keyboard)
          }
          res = await PaymentPasswordReset(params)
          if (res) {
            this.$toast.success('设置成功');
            setTimeout(() => {
              this.$router.go(-1)
            }, 1000)
          }
          break;
      }
    },
    // 初始化支付密码与忘记支付密码
    async getPay () {
      if (this.next == 1) {
        setTimeout(() => {
          this.password = this.keyboard
          this.KEYBOARD('')
          this.text = "请再次填写以确认"
          this.showBtn = true
        }, 600)
      }
      if (this.next > 1) {
        if (this.password == this.keyboard) {
          this.isdisabled = false
        } else {
          this.$toast('两次密码不一致');
        }
      }
    },
    // 修改支付密码
    async getChangePay () {
      let params = {
        payment_password: md5(this.keyboard)
      }
      if (this.next == 1) {
        // 校验当前支付密码
        let data = await PaymentPasswordCheck(params)
        if (data) {
          this.oldPassword = md5(this.keyboard)
          this.KEYBOARD('')
          this.text = "请设置新支付密码，用于支付验证"
        } else {
          this.next = 0
        }
      }

      if (this.next == 2) {
        this.password = this.keyboard
        this.KEYBOARD('')
        this.text = "确认支付密码"
        this.showBtn = true
      }

      if (this.next > 2) {
        if (this.password == this.keyboard) {
          this.isdisabled = false
        } else {
          this.$toast('两次密码不一致');
        }
      }
    }
  },
  computed: {
    ...mapState([
      'keyboard'
    ])
  },
  watch: {
    keyboard: function () {
      console.warn('forgrtPay')
      this.isdisabled = true
      if (this.keyboard.length >= 6) {
        let reg = /^(\d)\1{5}$/; // 不重复6位 类似111111,222222
        let str = '0123456789_9876543210'; // str.indexOf(value) > -1 不连续判断 类似123456

        if (reg.test(this.keyboard)) {
          this.$toast('密码不能为重复6位');
          return
        }
        if (str.indexOf(this.keyboard) > -1) {
          this.$toast('密码不能为连续数字');
          return
        }
        this.next++
        switch (getSessStore('pageType')) {
          case 'newPay':
            this.getPay()
            break;
          case 'forgetPay':
            this.getPay()
            break;
          case 'changePay':
            setTimeout(() => {
              this.getChangePay()
            }, 600)
            break;
        }
        // this.$router.push({ name: 'forget', params: { type: 'Password' } })
      }
    }
  }
}
</script>

<style scoped lang="scss">
@import "src/style/mixin";

main {
  .text {
    font-size: 0.34rem;
    margin-bottom: 0.8rem;
  }
  .code-input-main-item {
    @include wh(0.9rem, 0.9rem);
    line-height: 0.9rem;
    margin-right: 0.2rem;
    font-size: 0.5rem;
    display: inline-block;
    vertical-align: middle;
    i {
      @include wh(0.26rem, 0.26rem);
      @include center();
      top: 48%;
      left: 54%;
      display: block;
      border-radius: 50%;
      background: #333;
    }
  }
  .publicButton {
    margin-top: 1.3rem;
    width: 84%;
  }
}
</style>
