<template>
  <main class="main">
    <div class="bg"></div>
    <header-top headTitle="设置"> </header-top>
    <section class="banklist">
      <p class="border-bottom"></p>
      <ul class="addBank">
        <li class="border-bottom">
          账户名

          <i
            class="iconfont icon-shenqingqiyerenzheng"
            style="color: #ffa500; font-size:.3rem"
            v-if="bind_name.user_flag == 'VIP'"
          ></i>
          <i class="iconfont" style="font-size:.3rem">
            {{ bind_name.name }}
          </i>
        </li>
        <li class="border-bottom" @click="changePassword">
          修改登录密码
          <i class="iconfont icon-enter"></i>
        </li>
        <li @click="payPassword" class="border-bottom">
          修改支付密码
          <i class="iconfont icon-enter"></i>
        </li>
        <router-link
          :to="{ path: 'messageCode' }"
          tag="li"
          class="border-bottom"
        >
          忘记支付密码
          <i class="iconfont icon-enter"></i>
        </router-link>
      </ul>
      <footer>
        <button class="get-recharge  border-1" @click="exit">
          退出登录
        </button>
      </footer>
    </section>
  </main>
</template>

<script>
import headerTop from '../../components/head';
import { setSessStore, removeStore, getSessStore } from '@/config/common'

export default {
  data () {
    return {
      bind_name: getSessStore("bind_name") ? getSessStore("bind_name") : null,
    }
  },
  components: {
    headerTop
  },
  methods: {
    // 修改登录密码
    changePassword () {
      setSessStore('pageType', 'ChangePassword')
      this.$router.push({ path: '/forget' })
    },
    // 修改支付密码
    payPassword () {
      setSessStore('pageType', 'changePay')
      this.$router.push({ path: '/verificationCode' })
    },
    // 退出登录
    exit () {
      removeStore('token')
      removeStore('phone')
      this.$router.push({ path: '/' })
    }
  },
  watch: {

  }
}
</script>

<style lang="scss" scoped>
@import "src/style/mixin";

.main {
  padding-top: 0.92rem;
  background: #f6f6f6;
  .add {
    float: right;
    width: 0.8rem;
    height: 0.92rem;
    font-size: 0.68rem;
    color: #fff;
    line-height: 0.92rem;
    text-align: center;
  }
  p {
    font-size: 0.24rem;
    color: #f85f5f;
    text-align: center;
    height: 0.5rem;
    line-height: 0.5rem;
  }
  .banklist {
    .addBank {
      background: #fff;
      li {
        padding: 0 0.3rem;
        @include wh(100%, 0.9rem);
        line-height: 0.9rem;
        font-size: 0.32rem;
        i {
          font-size: 0.4rem;
          float: right;
        }
        &:active {
          background: #f4f4f4;
        }
      }
    }
    footer {
      padding: 0.65rem;
      position: fixed;
      bottom: 0;
      left: 0;
      width: 100%;
      .get-recharge {
        @include sc(0.3rem);
        @include wh(100%, 0.9rem);
        background: #fff;
        line-height: 0.8rem;
        border-radius: 0.1rem;
        text-align: center;
        &:active {
          background: #f4f4f4;
        }
        &:after {
          border-radius: 0.1rem;
        }
      }
    }
  }
  .bg {
    background: #f6f6f6;
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    z-index: -1;
  }
}
</style>
