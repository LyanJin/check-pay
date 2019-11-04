<template>
  <main>
    <!-- 注册与忘记密码 -->
    <div class="loginForm">
      <h1 v-if="type == 'Forget'">请填写您要找回密码的账号</h1>
      <h1 v-else>请输入你的手机号</h1>
      <ul class="clear">
        <li @click="show">
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
          <span class="delete right" v-if="phoneNumber" @click="userDelete">
            <i></i>
          </span>
        </li>
      </ul>
      <button
        class="publicButton"
        @click="next"
        :class="{ isdisabled: isdisabled }"
        :disabled="isdisabled"
      >
        下一步
      </button>
    </div>

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
import { numberCheck, forgetPassw } from '@/api/getData';
import { getSessStore } from '@/config/common'
import { mapState } from 'vuex'

export default {
  props: {
    type: null, // 提示语
  },
  data () {
    return {
      phoneNumber: null, // 手机号
      isdisabled: true, // 是否禁用输入账号按钮
      title: null,
      showPhone: false, // 弹出手机归属地页
      computedTime: -1   // 验证码倒计时
    }
  },
  components: {
    countryPhone,
    [Popup.name]: Popup,
  },
  computed: {
    ...mapState([
      'areaCode'
    ])
  },
  methods: {
    userDelete () {
      this.phoneNumber = null
    },
    async next () {
      let data
      if (this.areaCode.phone_code == '+86' && this.phoneNumber.length < 11) {
        this.$toast('你输入了无效的手机号，请重新输入');
        return
      }

      if (this.computedTime <= 0) {
        // 检测号码是否已存在
        if (getSessStore('pageType') == 'Registered') {
          data = await numberCheck({ "number": this.areaCode.phone_code + this.phoneNumber });
          if (data) {
            console.log(data)
            // 账号已存在
            if (data.error_code == '1017') {
              return this.$dialog.alert({
                message: data.message + ',前往登录！'
              }).then(() => {
                this.$router.go(-1)
              });
            }
          }
        } else
          if (getSessStore('pageType') == 'Forget') {
            data = await forgetPassw({ "number": this.areaCode.phone_code + this.phoneNumber });
          }
        if (data) {
          // 检测号码成功开始倒计时
          this.computedTime = 60
          this.timer = setInterval(() => {
            this.computedTime--;
            if (this.computedTime == 0) {
              clearInterval(this.timer)
            }
          }, 1000)
          this.$router.push({ name: 'verificationCode', params: { phone: this.phoneNumber } })
        }
      } else {
        this.$toast('您操作太频繁请等候' + this.computedTime + '秒！');
        let second = 3;
        const timer = setInterval(() => {
          second--;
          if (second) {
            this.$toast({
              duration: 0,       // 持续展示 toast
              forbidClick: true, // 禁用背景点击
              message: '您操作太频繁请等候' + this.computedTime + '秒！'
            });
          } else {
            clearInterval(timer);
            this.$toast.clear();
          }
        }, 1000);
      }
    },
    show () {
      this.showPhone = !this.showPhone
    },
  },
  watch: {
    phoneNumber: function () {
      if (this.phoneNumber && this.phoneNumber.length >= 8) {
        this.isdisabled = false
      } else {
        this.isdisabled = true
      }
    },
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
  }
  .van-popup--right {
    width: 100%;
  }
}
</style>
