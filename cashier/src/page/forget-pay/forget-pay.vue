<template>
  <main class="main">
    <header-top headTitle="忘记支付密码"></header-top>
    <div class="loginForm">
      <h1>验证身份信息用于找回密码 </br> <span>为了保障您的账号安全，请完成验证</span></h1>
      <ul class="clear">
        <li class="border-bottom">
          <input v-NoEmoji
            type="text"
            placeholder="**白（请输入完整姓名）"
            maxlength="11"
            v-model.trim="name"
          />
          <span class="delete right" v-if="name" @click="userDelete()">
            <i></i>
          </span>
        </li>
        <li class="border-bottom">
          <input v-NoEmoji
            type="tel"
            placeholder="请确保输入之前绑定的银行卡号"
            maxlength="11"
            v-model.trim="bankNumber"
          />
          <span class="delete right" v-if="bankNumber" @click="bankDelete()">
            <i></i>
          </span>
        </li>
      </ul>
      <button
        class="publicButton"
        @click="next()"
        :class="{ isdisabled: isdisabled }"
        :disabled="isdisabled"
      >
        验证身份
      </button>
    </div>
  </main>
</template>

<script>
import headerTop from '../../components/head'
import { setSessStore } from '@/config/common'

export default {
  data () {
    return {
      bankNumber: null, // 银行卡号
      name: null, // 用户名
      isdisabled: true, // 是否禁用输入账号按钮

    }
  },
  activated () {

  },
  components: {
    headerTop
  },
  methods: {
    userDelete () {
      this.name = null
      this.isdisabled = true
    },
    bankDelete () {
      this.bankNumber = null
      this.isdisabled = true
    },
    next () {
      setSessStore('pageType', 'forgetPay')
      this.$router.push({ path: '/verificationCode' })
    },
  },
  watch: {
    bankNumber: function () {
      if (this.name && this.bankNumber && this.bankNumber.length >= 9) {
        this.isdisabled = false
      } else {
        this.isdisabled = true
      }
    },
    name: function () {
      if (this.name && this.bankNumber && this.bankNumber.length >= 9) {
        this.isdisabled = false
      } else {
        this.isdisabled = true
      }
    }
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
      padding: 0.9rem 0;
      text-align: center;
      font-size: 0.34rem;
      span {
        color: #888;
        font-size: 0.28rem;
      }
    }
    ul {
      padding-bottom: 1.5rem;
      li {
        position: relative;
        @include sc(0.3rem);
        @include wh(100%, 1.1rem);
        line-height: 1.2rem;
        border-color: #aaa;
        input {
          @include wh(90%, 0.4rem);
          line-height: 0.4rem;
          margin-top: 0.4rem;
          background: transparent;
          font-size: 0.3rem;
        }
        .country {
          height: 1rem;
          color: #888;
          padding-right: 0.6rem;
          background: url("../../assets/icon/rigth.png") no-repeat right 0.36rem;
          background-size: 50% 50%;
          font-size: 0.28rem;
        }
        .delete {
          @include wh(9%, 1rem);
          i {
            display: inline-block;
            @include bis("../../assets/icon/copy.png");
            @include wh(0.48rem, 0.48rem);
            margin-top: 0.4rem;
          }
        }
      }
    }

    .ward {
      color: #f85f5f;
      font-size: 0.26rem;
      margin: 0.12rem 0;
    }
  }
}
</style>
