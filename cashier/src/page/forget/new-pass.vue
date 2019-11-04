<template>
  <main>
    <!-- 验证成功设置新密码 -->
    <div class="loginForm">
      <h1 v-html="textlist"></h1>
      <ul class="clear">
        <li for="oldPass" v-if="old">
          <input
            v-NoEmoji
            v-if="!showPassword"
            type="password"
            placeholder="请输入当前登录密码"
            v-model.trim="oldpassWord"
            maxlength="14"
            id="oldPass"
            @keydown.space.prevent
          />

          <input
            v-NoEmoji
            v-else
            type="text"
            placeholder="请输入当前登录密码"
            v-model.trim="oldpassWord"
            maxlength="14"
            id="oldPass"
            @keydown.space.prevent
          />

          <span class="look right" @click="changePassWordType">
            <i v-if="!showPassword"></i>
            <i v-else class="openEye"></i>
          </span>
        </li>

        <li for="pass" v-else>
          <input
            v-NoEmoji
            v-if="!showPassword"
            type="password"
            placeholder="6-14位，建议英文、数字、符号组合"
            v-model.trim="passWord"
            maxlength="14"
            id="pass"
            @keydown.space.prevent
          />

          <input
            v-NoEmoji
            v-else
            type="text"
            placeholder="6-14位，建议英文、数字、符号组合"
            v-model.trim="passWord"
            maxlength="14"
            id="pass"
            @keydown.space.prevent

          />
          <span class="look right" @click="changePassWordType">
            <i v-if="!showPassword"></i>
            <i v-else class="openEye"></i>
          </span>
        </li>
      </ul>

      <button
        v-if="old"
        class="publicButton"
        @click="next"
        :class="{ isdisabled: isdisabled2 }"
        :disabled="isdisabled2"
      >
        下一步
      </button>
      <button
        v-else
        class="publicButton"
        @click="newpass"
        :class="{ isdisabled: isdisabled }"
        :disabled="isdisabled"
      >
        保存新密码
      </button>
    </div>
  </main>
</template>

<script>
import { mapState } from 'vuex'
import { authRegister, forgetPasswReset, forgetChange, resetVerify } from '@/api/getData'
import { getSessStore } from '@/config/common'
import { setTimeout } from 'timers';
import md5 from 'js-md5';

export default {
  props: {
    text: null, // 提示语
    phone: null, // 手机号
    code: null, // 验证码
    old: false, // 输出旧密码
  },
  data () {
    return {
      textlist: this.text, // 提示语
      isdisabled: true, // 是否禁用设置密码按钮
      isdisabled2: true, // 是否禁用下一步
      showPassword: true, // 是否显示密码
      oldpassWord: null, // 旧密码
      passWord: null, // 密码

    }
  },
  components: {
  },
  computed: {
    ...mapState([
      'areaCode'
    ])
  },
  methods: {
    async next () {
      // 验证规则密码必须包含数字和字母
      let regExp = /^(?![^a-zA-Z]+$)(?!\D+$)/;
      if (!regExp.test(this.oldpassWord)) {
        this.$toast('密码必须包含数字和字母');
        return
      }
      let params = {
        "ori_password": md5(this.oldpassWord),
      }
      // 检查原密码是否正确
      let data = await resetVerify(params)
      if (data) {
        this.passWord = ''
        this.textlist = "请输入新密码"
        this.$emit('changeOld')
      }
    },
    async newpass () {
      // 验证规则密码必须包含数字和字母
      let regExp = /^(?![^a-zA-Z]+$)(?!\D+$)/;
      if (!regExp.test(this.passWord)) {
        this.$toast('密码必须包含数字和字母');
        return
      }

      // 判断是否为修改密码
      let data, params //注册账户设置密码
      if (getSessStore('pageType') == 'ChangePassword') {
        if (this.oldpassWord === this.passWord) {
          this.$toast('新密码不能与旧密码相同');
        } else {
          params = {
            "ori_password": md5(this.oldpassWord),
            "new_password": md5(this.passWord)
          }
          // 修改密码
          data = await forgetChange(params)
          if (data) {
            this.$toast.success('修改成功');
            setTimeout(() => {
              this.$router.replace({ name: 'login' })
            }, 1500)
          }
        }

      } else {
        params = {
          "number": this.areaCode.phone_code + this.phone,
          "auth_code": this.code,
          "password": md5(this.passWord)
        }
        if (getSessStore('pageType') == 'Password') {
          // 注册
          data = await authRegister(params)
        } else if (getSessStore('pageType') == 'ForgetPassword') {
          // 找回密码
          data = await forgetPasswReset(params)
        }
        if (data) {
          if (getSessStore('pageType') == 'Password') {
            this.$toast.success('注册成功');
          } else if (getSessStore('pageType') == 'ForgetPassword') {
            this.$toast.success('新登录密码设置成功');
          }
          setTimeout(() => {
            this.$router.replace({ name: 'login' })
          }, 1500)
        }
      }
    },
    // 是否显示密码
    async changePassWordType () {
      this.showPassword = !this.showPassword
    },

  },
  watch: {
    oldpassWord: function () {
      if (this.oldpassWord && this.oldpassWord.length >= 6) {
        this.isdisabled2 = false
      } else {
        this.isdisabled2 = true
      }
    },
    passWord: function () {
      if (this.passWord && this.passWord.length >= 6) {
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

main {
  .loginForm {
    padding: 0 0.65rem;
    h1 {
      padding-top: 0.6rem;
      padding-bottom: 0.2rem;
      text-align: center;
      font-size: 0.34rem;
    }
    ul {
      padding-bottom: 1.5rem;
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
    }
  }
}
</style>
