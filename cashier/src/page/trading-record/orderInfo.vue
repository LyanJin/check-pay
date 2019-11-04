<template>
  <main class="main" v-if="data">
    <header-top headTitle="交易详情"></header-top>
    <section class="border-bottom order-center">
      <p>{{ data.order_type }}</p>
      <div :class="{ amount: Number(data.amount) > 0 }">
        {{ data.amount | NumFormat }}
      </div>
      <span>{{ data.status }}</span>
    </section>

    <section class="order-info">
      <p v-if="data.pay_method">
        <label>支付方式</label>
        <span>{{ data.pay_method }}</span>
      </p>
      <p v-if="data.bank_info">
        <label>提现到</label>
        <span>{{ data.bank_info }}</span>
      </p>
      <p v-if="data.in_account">
        <label>收款人</label>
        <span>{{ data.in_account }}</span>
      </p>
      <p v-if="data.comment">
        <label>备注</label>
        <span>{{ data.comment }}</span>
      </p>
      <p v-if="data.out_account">
        <label>出款人</label>
        <span>{{ data.out_account }}</span>
      </p>
      <p v-if="data.create_time">
        <label>创建时间</label>
        <span>{{ data.create_time }}</span>
      </p>
      <p v-if="data.fee">
        <label>手续费</label>
        <span>{{ data.fee }}元</span>
      </p>
      <p v-if="data.tx_id">
        <label>订单号</label>
        <span class="ellipsis" style="width: 66%;">
          {{ data.tx_id }}
        </span>
        <button @click="copy(data.tx_id)">复制</button>
      </p>
    </section>

    <footer class="service">
      <span @click="service">
        对交易有疑问？
      </span>
    </footer>
  </main>
</template>

<script>
import headerTop from '../../components/head'
import { getSessStore } from '@/config/common'

export default {
  data () {
    return {
      data: null
    }
  },
  activated () {
    if (this.$route.params.data) {
      this.data = this.$route.params.data
    } else {
      this.$router.go(-1)
    }
  },
  components: {
    headerTop
  },
  methods: {
    // 点击复制
    copy (data) {
      console.warn(data)
      let textArea = document.createElement("textarea");
      textArea.style.position = 'fixed';
      textArea.style.top = '0';
      textArea.style.left = '0';
      textArea.style.width = '2px';
      textArea.style.height = '2px';
      textArea.value = data;
      document.body.appendChild(textArea);
      if (navigator.userAgent.match(/iphone|ipad|ipod/i)) { // iOS browser
        textArea.setSelectionRange(0, 9999);
        console.warn('ios')
      } else {
        textArea.select();
        console.warn('android')
      }
      try {
        let successful = document.execCommand('copy');
        if (successful) {
          this.$toast('复制成功')
        } else {
          this.$toast('该浏览器不支持点击复制')
        }
      } catch (err) {
        this.$toast('该浏览器不支持点击复制')
      }
      document.body.removeChild(textArea);
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
.main {
  padding: 0.65rem;
  padding-top: 0.92rem;
  .order-center {
    text-align: center;
    font-size: 0.32rem;
    padding: 0.6rem;
    div {
      font-size: 0.5rem;
      &:before {
        content: "-";
        display: inline-block;
        line-height: 0.64rem;
        vertical-align: top;
      }
    }
    .amount {
      color: #e08c00;
      &:before {
        content: "+";
      }
    }
    span {
      font-size: 0.28rem;
      color: #888;
    }
  }
  .order-info {
    color: #888;
    font-size: 0.3rem;
    p {
      padding-top: 0.6rem;
      label {
        width: 22%;
        display: inline-block;
      }
      span {
        display: inline-block;
        width: 74%;
        vertical-align: top;
        color: #333;
      }
      button {
        width: 10%;
        float: right;
        color: #3367ec;
        background: transparent;
      }
    }
  }
  .service {
    width: 100%;
    position: absolute;
    bottom: 0.6rem;
    left: 0;
    text-align: center;
    margin-top: 0.32rem;
    margin-bottom: 0.1rem;
    font-size: 0.26rem;
    color: #3367ec;
  }
}
</style>
