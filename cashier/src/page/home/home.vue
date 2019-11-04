<template>
  <main class="main" ref="homePage">
    <div class="total-gold">
      <p>可用金币</p>
      <div class="gold ellipsis">{{ balance | NumFormat }}</div>
    </div>

    <!-- 首页菜单 -->
    <ul class="home-list">
      <li
        :class="{ disable: permissions.indexOf('DEPOSIT') == -1 }"
        @click="payment('recharge', 'DEPOSIT')"
      >
        <img src="../../assets/image/cz.png" alt="" />
        <div>
          充值 <br />
          <span>钱包余额充值</span>
        </div>
      </li>
      <li
        :class="{ disable: permissions.indexOf('WITHDRAW') == -1 }"
        @click="payment('withdrawal', 'WITHDRAW')"
      >
        <img src="../../assets/image/tx.png" alt="" />
        <div>
          提现 <br />
          <span>快速到账</span>
        </div>
      </li>
      <li
        :class="{ disable: permissions.indexOf('TRANSFER') == -1 }"
        @click="payment('transfer', 'TRANSFER')"
      >
        <img src="../../assets/image/zz.png" alt="" />
        <div>
          转账 <br />
          <span>免手续费</span>
        </div>
      </li>
      <li
        :class="{ disable: permissions.indexOf('BINDCARD') == -1 }"
        @click="payment('bankCard', 'BINDCARD')"
      >
        <img src="../../assets/image/yhk.png" alt="" />
        <div>
          银行卡 <br />
          <span>添加银行卡</span>
        </div>
      </li>
      <li @click="payment('tradingRecord')">
        <img src="../../assets/image/zd.png" alt="" />
        <div>
          账单 <br />
          <span>交易明细</span>
        </div>
      </li>

      <li @click="payment('setting')">
        <img src="../../assets/image/sz.png" alt="" />
        <div>
          设置 <br />
          <span>安全设置</span>
        </div>
      </li>
    </ul>

    <footer class="service">
      <span @click="service">
        <i class="iconfont icon-kefu"></i>
        我的客服
      </span>
    </footer>
  </main>
</template>

<script>
import { getSessStore, setSessStore } from '@/config/common'
import { balanceGet } from '@/api/getData'

export default {
  data () {
    return {
      balance: '0', // 金币数
      has_trade_pwd: null, // 是否添加支付密码
      token: null,
      clientHeight: null,
      permissions: getSessStore('permissions'),
    }
  },

  async activated () {
    console.warn(this.permissions.indexOf('DEPOSIT') == -1)
    // 获取当前余额
    const res = await balanceGet()
    if (res) {
      this.balance = res.data.balance
      this.has_trade_pwd = res.data.has_trade_pwd
    }
  },
  mounted () {
    // 获取浏览器可视区域高度
    if (this.$refs.homePage.clientHeight < Number(`${document.documentElement.clientHeight}`)) {
      this.$refs.homePage.style.height = '100vh'
    }
  },
  components: {

  },
  methods: {
    // 判断是否已设置支付密码
    payment (url, permiss = 'all') {
      // 判断是否有权限
      if (permiss == 'all' || this.permissions.indexOf(permiss) != -1) {
        if (!this.has_trade_pwd) {
          this.$dialog.confirm({
            message: '您还未设置支付密码,前往设置支付密码！'
          }).then(() => {
            setSessStore('pageType', 'newPay')
            this.$router.push({ path: '/verificationCode' })
          }).catch(() => { });
        } else {
          this.$router.push({ path: url })
        }
      }

    },
    // 联系客服
    service () {
      console.warn(getSessStore('service_url'))
      if (getSessStore('service_url')) {
        window.open(getSessStore('service_url'))
      } else {
        this.$toast('系统维护中，尽情期待！');
      }
    }

  }
} 
</script>

<style scoped lang="scss">
@import "../../style/mixin";
.main {
  padding: 0 0.3rem;
  background: url("../../assets/image/sybg.png") no-repeat;
  background-color: $maincolor;
  background-size: 100% 100%;

  .total-gold {
    width: 100%;
    padding: 1.2rem 0.2rem 0.58rem;
    font-size: 0.9rem;
    color: #fff;
    p {
      font-size: 0.3rem;
      color: #fff;
    }
    .gold {
      color: #fff;
    }
  }
  .home-list {
    width: 100%;
    background: #fff;
    border-radius: 0.3rem;
    padding-top: 0.24rem;
    li {
      width: 49%;
      display: inline-block;
      text-align: center;
      margin-bottom: 0.24rem;

      img {
        @include wh(1.5rem, 1.3rem);
      }
      div {
        color: #333;
        font-size: 0.28rem;
        span {
          font-size: 0.24rem;
          color: #888;
        }
      }
    }
    .disable {
      opacity: 0.4;
    }
  }
  .service {
    text-align: center;
    margin-top: 0.32rem;
    margin-bottom: 0.1rem;
    font-size: 0.24rem;
    color: #eaefff;
    .iconfont {
      color: #fff;
    }
  }
}
</style>
