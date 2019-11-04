<template>
  <main class="main">
    <div class="bg"></div>
    <header-top headTitle="银行卡管理"> </header-top>
    <section class="banklist">
      <p class="border-bottom"></p>
      <div class="bank" v-if="bankInfo">
        {{ bankInfo.bank_name }}
        ({{ bankInfo.card_no.substr(bankInfo.card_no.length - 4) }})
        <span class="right" @click="showBinding">解除绑定</span>
      </div>
    </section>
    <!-- 确定解除绑定 -->
    <van-popup
      class="confirmBox"
      v-model="binding"
      position="bottom"
      :overlay="true"
    >
      <footer>
        <div>
          <p class="text border-bottom">解除绑定后银行卡将不可使用</p>
          <p class="confirm" @click="showPayPassword()">确定解除绑定</p>
        </div>
        <button @click="showBinding()">取消</button>
      </footer>
    </van-popup>

    <!-- 输入支付密码 -->
    <van-popup v-model="payPassword" position="bottom" :overlay="true">
      <pay-password
        :show="true"
        @successPassword="deleteBank"
        @hide="
          () => {
            payPassword = false;
          }
        "
      ></pay-password>
    </van-popup>
  </main>
</template>

<script>
import headerTop from '../../components/head';
import { Popup } from 'vant';
import payPassword from '../../components/pay-password'
import { mapMutations, mapState } from 'vuex'
import { bankcardDelete } from '@/api/getData'
import md5 from 'js-md5';

export default {
  name: "bankAdmin",
  data () {
    return {
      binding: false, //确定解除绑定
      payPassword: false,//输入支付密码
      bankInfo: null, // 银行卡信息
    }
  },
  created () {
    if (this.$route.params.data && this.$route.params.length) {
      this.bankInfo = this.$route.params.data
    } else {
      this.$router.go(-1)
    }
    console.warn(this.$route.params.data)
  },
  components: {
    headerTop,
    payPassword,
    [Popup.name]: Popup
  },
  methods: {
    ...mapMutations([
      'KEYBOARD'
    ]),
    // 删除银行卡
    async deleteBank () {
      let params = {
        "payment_password": md5(this.keyboard),
        "bank_card_id": this.bankInfo.id
      }
      const data = await bankcardDelete(params)
      console.warn(data)
      if (data) {
        this.$toast.success('解除成功');
        setTimeout(() => {
          this.$router.go(-1)
        }, 1500)
      }
    },

    showBinding () {
      console.warn(this.$route.params.length)
      if (this.$route.params.length > 1) {
        this.binding = !this.binding
      } else {
        this.$toast('至少绑定一张银行卡,如有需要请联系客服！');
      }

    },
    showPayPassword () {
      this.showBinding()
      this.payPassword = !this.payPassword
    }
  },
  computed: {
    ...mapState([
      'keyboard'
    ])
  },
}
</script>

<style lang="scss" scoped>
@import "src/style/mixin";

.main {
  padding-top: 0.92rem;
  background: #f6f6f6;
  p {
    font-size: 0.24rem;
    text-align: center;
    height: 0.5rem;
    line-height: 0.5rem;
  }
  .banklist {
    .bank {
      font-size: 0.32rem;
      background: #fff;
      height: 1rem;
      line-height: 1rem;
      padding: 0 0.3rem;
      span {
        color: #f85f5f;
      }
    }
  }

  .confirmBox {
    background: transparent;
    padding: 0.25rem;
  }
  footer {
    div {
      background: rgba(252, 252, 252, 0.8);
      border-radius: 0.24rem;
      p {
        height: 0.9rem;
        line-height: 0.9rem;
      }
      .text {
        font-size: 0.28rem;
        color: #888;
      }
      .confirm {
        font-size: 0.34rem;
        color: #f85f5f;
      }
    }
    button {
      background: rgba(252, 252, 252, 0.8);
      border-radius: 0.24rem;
      height: 0.88rem;
      line-height: 0.88rem;
      width: 100%;
      margin-top: 0.2rem;
      font-size: 0.34rem;
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
