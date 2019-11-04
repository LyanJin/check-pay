<template>
  <main v-if="show">
    <!-- <div class="bg" @click="hide()"></div> -->
    <section class="payPassword ">
      <h3 class="border-bottom">
        <i class="iconfont icon-guanbi" @click="hide()"></i>
        请输入支付密码
      </h3>
      <div class="money" v-if="money"><em>￥</em>{{ money | NumFormat }}</div>
      <div class="text" v-else>请输入支付密码，以验证身份</div>
      <div class="code-input-main">
        <span
          class="code-input-main-item border-1"
          for="code"
          v-for="(value, index) in length"
          :key="value"
        >
          <i v-if="keyboard[index]"></i>
        </span>
        <p class="clear">
          <router-link :to="{ path: '/messageCode' }" tag="span">
            忘记密码？
          </router-link>
        </p>
      </div>
      <Keyboard :show="true" :length="6"></Keyboard>
    </section>
  </main>
</template>

<script>
import Keyboard from './Keyboard';
import { mapState } from 'vuex'
import { withdrawOrderCreate, PaymentPasswordCheck } from '@/api/getData'
import md5 from 'js-md5';

export default {
  props: {
    show: {
      type: Boolean,
      default: false
    },
    money: null,
    user_bank: null,
  },
  data () {
    return {
      length: 6,    //密码位数
    }
  },
  components: {
    Keyboard
  },
  computed: {
    ...mapState([
      'keyboard'
    ])
  },
  methods: {
    hide () {
      this.$emit('hide')
    },
    async orderCreate () {
      // 校验支付密码
      const data = await PaymentPasswordCheck({ payment_password: md5(this.keyboard) })
      if (data) {
        this.hide()
        this.$emit('successPassword')
      }
    }
  },
  watch: {
    keyboard: function () {
      if (this.keyboard.length >= 6) {
        this.orderCreate()
      }
    }
  }
}

</script>

<style lang="scss" scoped>
@import "../style/mixin";

main {
  .payPassword {
    h3.border-bottom {
      @include wh(100%, 0.84rem);
      line-height: 0.84rem;
      text-align: center;
      font-size: 0.34rem;
      i {
        @include wh(1rem, 0.84rem);
        position: absolute;
        left: 0;
        top: 0;
        color: #ccc;
        font-size: 0.36rem;
      }
      &::after {
        border-color: #f0f0f0;
      }
    }
    .money {
      text-align: center;
      font-size: 0.8rem;
      height: 1.6rem;
      line-height: 1.6rem;
      margin-bottom: 0.2rem;
      em {
        font-size: 0.5rem;
        vertical-align: top;
      }
    }
    .text {
      text-align: center;
      font-size: 0.28rem;
      height: 1.6rem;
      line-height: 1.6rem;
      margin-bottom: 0.2rem;
    }
    .code-input-main {
      text-align: center;
      .code-input-main-item {
        width: 0.9rem;
        height: 0.9rem;
        line-height: 0.7rem;
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
      p {
        padding: 0.2rem 0.2rem 0 0.2rem;
        span {
          float: right;
          padding: 0.2rem;
          color: #609fff;
          font-size: 0.28rem;
        }
      }
    }
    .keyboard {
      position: relative;
      margin-top: 0.2rem;
    }
  }
}
</style>
