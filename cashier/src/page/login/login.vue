<template>
  <main class="main">
    <section class="loginForm">
      <h1>手机号登录</h1>
      <ul class="clear">
        <li @click="show()">
          {{ areaCode.cn }}
          <span class="right country"> {{ areaCode.phone_code }}</span>
        </li>
        <li>
          <input
            v-NoEmoji
            v-numberOnly
            type="tel"
            placeholder="请输入手机号码"
            maxlength="11"
            v-model.trim="phoneNumber"
          />
          <span class="delete right" v-if="phoneNumber" @click="userDelete()">
            <i></i>
          </span>
        </li>
        <li for="pass" class="passlist">
          <input
            v-NoEmoji
            v-if="!showPassword"
            type="password"
            placeholder="请输入密码"
            v-model.trim="passWord"
            maxlength="14"
            id="pass"
          />
          <input
            v-NoEmoji
            v-else
            type="text"
            placeholder="请输入密码"
            v-model.trim="passWord"
            maxlength="14"
            id="pass"
          />
          <span class="look right" @click="changePassWordType">
            <i v-if="!showPassword"></i>
            <i v-else class="openEye"></i>
          </span>
          <span class="delete right" v-if="passWord" @click="passDelete()">
            <i></i>
          </span>
        </li>
      </ul>
      <button
        class="publicButton"
        @click="Login"
        :class="{ isdisabled: isdisabled }"
        :disabled="isdisabled"
      >
        登录
      </button>
      <p class="to_forget">
        <a @click="forgetPass"> 忘记密码？</a>
      </p>
    </section>
    <footer>
      <div>
        没有账户？
        <a @click="getRegister"> 快速注册</a>
      </div>
    </footer>

    <!-- 手机归属地 -->
    <van-popup v-model="showPhone" position="right" :overlay="false">
      <countryPhone
        :show="true"
        @hide="
          () => {
            showPhone = false;
          }
        "
      ></countryPhone>
    </van-popup>
  </main>
</template>

<script>
import countryPhone from '../../components/country-phone';
import { Popup } from 'vant';
import { mapState } from 'vuex'
import { authLogin, userTest } from '@/api/getData'
import { setSessStore, getSessStore } from '@/config/common'
import md5 from 'js-md5';

export default {
  data () {
    return {
      phoneNumber: null, // 手机号
      passWord: null, // 密码
      showPassword: false, // 是否显示密码
      isdisabled: true, // 是否禁用登录按钮
      showPhone: false, // 弹出手机归属地页
    }
  },
  components: {
    countryPhone,
    [Popup.name]: Popup
  },
  computed: {
    ...mapState([
      'areaCode'
    ])
  },
  methods: {
    // 是否显示密码
    changePassWordType () {
      this.showPassword = !this.showPassword
    },
    // 手机号清空
    userDelete () {
      this.phoneNumber = null
    },
    // 密码清空
    passDelete () {
      this.passWord = null
    },
    show () {
      this.showPhone = !this.showPhone
    },


    // 密码登录
    async Login () {
      let params = {
        "number": this.areaCode.phone_code + this.phoneNumber,
        "password": md5(this.passWord)
      }
      let data = await authLogin(params)
      if (data) {
        // 登录成功更新token
        setSessStore('token', data.data.token)
        // 用户当前手机号
        setSessStore('phone', { area: this.areaCode.phone_code, phone: this.phoneNumber })
        // 客服链接地址
        setSessStore('service_url', data.data.service_url)
        // 拥有权限
        setSessStore('permissions', data.data.permissions)
        // 账户名
        setSessStore('bind_name', { name: data.data.bind_name, user_flag: data.data.user_flag })
        // 成功后清空账号密码
        this.phoneNumber = null
        this.passWord = null
        this.$router.replace({ name: 'home' })
      }
    },


    isdisabledfun () {
      // 密码不能少于6位必须包含数字和字母
      let regExp = /^(?![^a-zA-Z]+$)(?!\D+$)/;
      if (this.phoneNumber && this.passWord && this.phoneNumber.length >= 6 && this.passWord.length >= 6 && regExp.test(this.passWord)) {
        this.isdisabled = false
      } else {
        this.isdisabled = true
      }
    },
    // 前往注册
    getRegister () {
      // 更新页面类型
      setSessStore('pageType', 'Registered')
      this.$router.push({ path: '/forget' })
    },
    // 忘记密码
    forgetPass () {
      setSessStore('pageType', 'Forget')
      this.$router.push({ path: '/forget' })
    }
  },
  watch: {
    passWord: function () {
      this.isdisabledfun()
    },
    phoneNumber: function () {
      this.isdisabledfun()

    }
  }
}
</script>

<style scoped lang="scss">
@import "../../style/mixin";

.main {
  .loginForm {
    padding: 0 0.65rem;
    h1 {
      padding-top: 1.2rem;
      text-align: center;
      font-size: 0.5rem;
    }
    ul {
      li {
        position: relative;
        @include sc(0.3rem);
        @include wh(100%, 1.1rem);
        line-height: 1.2rem;
        border-bottom: 0.01rem solid #999;
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
        .look {
          @include wh(9%, 1rem);
          i {
            display: inline-block;
            @include bis("../../assets/icon/eye.png");
            @include wh(0.48rem, 0.48rem);
            margin-top: 0.4rem;
          }
          .openEye {
            @include bis("../../assets/icon/eyeopen.png");
          }
        }
      }
      .passlist {
        input {
          @include wh(80%, 0.4rem);
          line-height: 0.4rem;
          margin-top: 0.4rem;
          background: transparent;
          font-size: 0.3rem;
        }
      }
    }
    .to_forget {
      padding-top: 0.1rem;
      a {
        color: #3367ec;
        font-size: 0.26rem;
      }
    }
  }
  footer {
    position: absolute;
    bottom: 0;
    left: 0;
    @include wh(100%, 2.15rem);
    @include bis("../../assets/image/dw.png");
    font-size: 0.26rem;
    div {
      text-align: center;
      margin-top: 0.4rem;
      color: #888;
      a {
        color: #3367ec;
      }
    }
  }
  .van-popup--right {
    width: 100%;
  }
}
</style>
