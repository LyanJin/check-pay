<template>
  <main class="main">
    <header-top headTitle="转账"></header-top>
    <ul class="clear">
      <li class="border-bottom user">
        转账给：
        <div class="logo">
          <i
            class="iconfont icon-shenqingqiyerenzheng"
            v-if="$route.params.is_auth"
          ></i>
          <img src="../../assets/image/default.png" alt="" />
        </div>
        {{ phone }}
      </li>
      <li>
        转账金额
        <span class="right"
          >可用余额 <em>￥{{ balance | NumFormat }}</em></span
        >
      </li>
      <li class="money border-bottom">
        <input
          v-NoEmoji
          class=""
          type="tel"
          placeholder="请输入转账金额"
          maxlength="8"
          v-price
          v-model.trim="money"
          @keydown.space.prevent
        />
      </li>
      <li>
        <van-field
          v-model="explain"
          clearable
          maxlength="20"
          placeholder="添加转账说明（20字以内）"
        />
      </li>
      <li>
        <button
          class="publicButton"
          @click="
            () => {
              if (
                $route.params.transfer_limit != 0 &&
                money > $route.params.transfer_limit
              ) {
                this.$toast('单笔交易最多' + $route.params.transfer_limit);
                return;
              }
              this.showDialog = !this.showDialog;
            }
          "
          :class="{ isdisabled: isdisabled }"
          :disabled="isdisabled"
        >
          确认转账
        </button>
      </li>
    </ul>

    <!-- 输入支付密码 -->
    <van-popup v-model.trim="show" position="bottom" :overlay="true">
      <pay-password
        :show="true"
        @successPassword="successPassword"
        @hide="
          () => {
            show = false;
          }
        "
      ></pay-password>
    </van-popup>

    <van-dialog
      v-model="showDialog"
      confirm-button-text="确认无误"
      show-cancel-button
      @confirm="
        () => {
          this.show = !this.show;
        }
      "
    >
      <div class="van-dialog-content">
        <div class="title">为避免转错账请确认对方账户信息后再转</div>
        <div class="message">
          转给：<em>{{ phone }}</em>
        </div>
        <div class="message" v-if="explain">
          备注：<em>{{ explain }}</em>
        </div>
      </div>
    </van-dialog>
  </main>
</template>

<script>

import headerTop from '../../components/head'
import payPassword from '../../components/pay-password'
import { Popup, Field } from 'vant';
import { mapState } from 'vuex'
import md5 from 'js-md5';
import { balanceGet, transferTransfer } from '@/api/getData'

export default {
  name: "transferMoney",
  data () {
    return {
      money: null,
      balance: null,  //可用余额
      phone: null,  //转账号码
      isdisabled: true, // 是否禁用充值按钮
      show: false,  //弹出确认付款
      showDialog: false,  //二次确认
      explain: null  //转账说明
    }
  },
  async created () {
    if (this.$route.params.phone) {
      this.phone = this.$route.params.phone
      // 获取当前余额
      const res = await balanceGet()
      if (res) {
        this.balance = res.data.balance
      }
    } else {
      this.$router.go(-1)
    }
  },
  components: {
    headerTop,
    [Popup.name]: Popup,
    [Field.name]: Field,
    payPassword
  },
  computed: {
    ...mapState([
      'keyboard',
      'areaCode'
    ])
  },
  methods: {
    async successPassword () {
      let params = {
        amount: this.money,
        zone: this.areaCode.phone_code,
        number: this.phone,
        comment: this.explain,
        payment_password: md5(this.keyboard)
      }

      const data = transferTransfer(params)
      if (data) {
        this.$toast.success('转账成功');
        setTimeout(() => {
          this.$router.go(-2)
        }, 1000)
      }
    },

  },
  watch: {
    money: function () {
      if (this.money > 0 && this.money <= Number(this.balance)) {
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
  padding-top: 0.92rem;
  .clear {
    padding: 0 0.65rem;
    li {
      font-size: 0.28rem;
      .right {
        color: #888;
        font-size: 0.24rem;
      }
    }
    .user {
      margin-bottom: 0.6rem;
      margin-top: 0.8rem;
      font-size: 0.3rem;
      height: 1rem;
      line-height: 1rem;
      .logo {
        position: relative;
        line-height: 0.4rem;
        text-align: center;
        vertical-align: middle;
        margin-right: 0.2rem;
        .iconfont {
          font-size: 0.42rem;
          color: #ffa500;
          position: absolute;
          bottom: -8px;
          right: -8px;
          font-size: 0.4rem;
        }
        p {
          font-size: 0.05rem;
          line-height: 0.2rem;
        }
        img {
          @include wh(0.64rem, 0.64rem);
          vertical-align: middle;
        }
      }
      div {
        display: inline-block;
      }
    }
    .money {
      margin-top: 0.16rem;
      padding: 0.1rem 0;
      padding-left: 0.6rem;
      &::before {
        content: "￥";
        font-size: 0.5rem;
        position: absolute;
        left: 0;
        bottom: 0.06rem;
      }
      input {
        width: 100%;
        font-size: 0.5rem;
      }
    }
  }
  .publicButton {
    margin-top: 0.58rem;
  }
  .van-dialog-content {
    padding: 0.64rem 0.9rem;
    text-align: center;
    font-size: 0.32rem;
    color: #333;
    .title {
      margin-bottom: 0.4rem;
    }
    .message {
      font-size: 0.36rem;
      em {
        color: #000;
      }
    }
  }
}
</style>
