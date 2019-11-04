<template>
  <main class="main">
    <header-top headTitle="提现"></header-top>
    <section v-if="limit_min > 0">
      <h4>单笔提现金额最低{{ limit_min }}元起，最高{{ limit_max }}元</h4>
      <ul class="clear">
        <li class="bank border-bottom" @click="chooseBank" v-if="bankData">
          <img v-if="bankData.value == 1" src="../../assets/bank/BOC.png" />
          <img v-if="bankData.value == 2" src="../../assets/bank/ICBC.png" />
          <img v-if="bankData.value == 3" src="../../assets/bank/PSBC.png" />
          <img v-if="bankData.value == 5" src="../../assets/bank/CMB.png" />
          <img v-if="bankData.value == 4" src="../../assets/bank/CCB.png" />
          <img v-if="bankData.value == 6" src="../../assets/bank/ABC.png" />
          <img v-if="bankData.value == 7" src="../../assets/bank/SPDB.png" />
          <img v-if="bankData.value == 8" src="../../assets/bank/CMBC.png" />
          <img v-if="bankData.value == 9" src="../../assets/bank/pa.png" />
          <img v-if="bankData.value == 10" src="../../assets/bank/HB.png" />
          <img v-if="bankData.value == 11" src="../../assets/bank/CITIC.png" />
          <img v-if="bankData.value == 12" src="../../assets/bank/CEB.png" />
          <img v-if="bankData.value == 13" src="../../assets/bank/CIB.png" />
          <img v-if="bankData.value == 14" src="../../assets/bank/GDB.png" />
          <img v-if="bankData.value == 15" src="../../assets/bank/BCM.png" />
          <div>
            <p class="name ellipsis">
              {{ bankData.name }}
              ({{ bankData.card_no.substr(bankData.card_no.length - 4) }})
            </p>
            <p class="ellipsis">预计2小时到账</p>
          </div>
          <span class="iconfont icon-you"></span>
        </li>
        <li>
          提现金额
        </li>
        <li class="money border-bottom">
          <input
            v-NoEmoji
            class=""
            type="tel"
            placeholder="请输入提现金额"
            maxlength="8"
            v-price
            v-model.trim="money"
            @keydown.space.prevent
          />
        </li>
        <li class="allmoney">
          <span
            >可用余额 ￥<em>{{ balance | NumFormat }}</em></span
          >
          <span class="all right" @click="allCarry">全部提现</span>
        </li>
        <li>
          <button
            class="publicButton"
            @click="next"
            :class="{ isdisabled: isdisabled }"
            :disabled="isdisabled"
          >
            立即提现
          </button>
        </li>
      </ul>
    </section>

    <!-- 选择银行卡 -->
    <van-popup v-model="show" position="bottom" :overlay="true">
      <choose-bank
        :show="true"
        :bankList="bankList"
        @hide="
          () => {
            show = false;
          }
        "
        @getbank="getbank"
      ></choose-bank>
    </van-popup>

    <!-- 输入提现密码 -->
    <van-popup v-model="payShow" position="bottom" :overlay="true">
      <pay-password
        :show="true"
        :money="money"
        :user_bank="bankData"
        @successPassword="successPassword"
        @hide="
          () => {
            payShow = false;
          }
        "
      ></pay-password>
    </van-popup>
  </main>
</template>

<script>
import { Popup } from 'vant';
import headerTop from '../../components/head'
import chooseBank from '../../components/choose-bank'
import payPassword from '../../components/pay-password'
import { mapState } from 'vuex'
import md5 from 'js-md5';
import { withdrawTypeList, bankcardList, withdrawOrderCreate } from '@/api/getData'
import { setTimeout } from 'timers';

export default {
  name: "withdrawal",
  data () {
    return {
      money: null,
      limit_min: 0,
      limit_max: 0,
      bankData: null,
      isdisabled: true,   // 是否禁用充值按钮
      show: false,         //弹出确认付款
      payShow: false,     //弹出确认付款
      balance: 0,     //当前余额
      bankList: null,     //当前余额
    }
  },
  async created () {
    // 获取用户银行卡列表
    const data = await bankcardList()
    if (data) {
      this.bankList = data.data.bankcards
      if (this.bankList.length > 0) {
        // 展示默认银行卡
        this.getbank(this.bankList[0])
      } else {
        this.$dialog.alert({
          message: '您还未添加银行卡,前往添加银行卡！'
        }).then(() => {
          this.$router.replace({ path: '/bankCard' })
        });
      }
    }
    // 获取配置信息
    let limit = await withdrawTypeList()
    if (limit) {
      this.limit_min = limit.data.limit_min
      this.limit_max = limit.data.limit_max
      this.balance = limit.data.balance
    }
  },
  computed: {
    ...mapState([
      'keyboard'
    ])
  },
  components: {
    [Popup.name]: Popup,
    headerTop,
    chooseBank,
    payPassword
  },
  methods: {
    userDelete () {
      this.phoneNumber = null
    },
    chooseBank () {
      this.show = !this.show
    },
    next () {
      this.payShow = !this.payShow
    },
    // 是否显示密码
    changePassWordType () {
      this.showPassword = !this.showPassword
    },
    getbank (data) {
      console.warn(data)
      if (data) {
        this.bankData = {
          id: data.id,
          name: data.bank_name,
          value: data.bank_idx,
          card_no: data.card_no
        }
      }
    },
    // 全部提现
    allCarry () {
      if (Number(this.balance) <= Number(this.limit_max)) {
        this.money = Number(this.balance)
      } else {
        this.money = Number(this.limit_max)
      }
    },
    // 提交提现请求
    async successPassword () {
      let params = {
        amount: this.money,
        user_bank: this.bankData.id,
        trade_password: md5(this.keyboard)
      }
      // 提交提现请求
      const data = await withdrawOrderCreate(params)
      if (data) {
        this.$router.push({ path: '/success' })
      }
    }
  },
  watch: {
    money: function () {
      if (this.money > 0 && this.money >= Number(this.limit_min) && this.money <= Number(this.limit_max)) {
        // 判断余额是否足够
        if (Number(this.balance) >= this.money) {
          this.isdisabled = false
        }
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
  h4 {
    background: #f4f4f4;
    font-size: 0.24rem;
    @include wh(100%, 0.6rem);
    line-height: 0.6rem;
    text-align: center;
    margin-bottom: 0.8rem;
  }
  .clear {
    padding: 0 0.65rem;
    li {
      font-size: 0.28rem;
      &.allmoney {
        font-size: 0.24rem;
        padding: 0.12rem 0;
        .all {
          color: #609fff;
        }
      }
    }
    .bank {
      margin-top: 0.16rem;
      padding: 0.1rem 0;
      margin-bottom: 0.6rem;
      img {
        @include wh(0.7rem, 0.7rem);
        vertical-align: top;
      }
      div {
        display: inline-block;
        padding: 0 0.1rem;
        width: 80%;
        p {
          font-size: 0.24rem;
          color: #888;
          &.name {
            font-size: 0.3rem;
            color: #333;
          }
        }
      }
      span {
        float: right;
        font-size: 0.4rem;
        color: #999;
        line-height: 0.8rem;
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
        bottom: 0.08rem;
      }
      input {
        width: 100%;
        font-size: 0.5rem;
      }
      ::-webkit-input-placeholder {
        font-size: 0.46rem;
      }
      ::-moz-placeholder {
        font-size: 0.46rem;
      } /* firefox 19+ */
      :-ms-input-placeholder {
        font-size: 0.46rem;
      } /* ie */
      input:-moz-placeholder {
        font-size: 0.46rem;
      }
    }
  }
  .publicButton {
    margin-top: 0.33rem;
    @include sc(0.3rem, #fff);
    background-color: #3367ec;
    @include wh(100%, 0.8rem);
    line-height: 0.8rem;
    border-radius: 0.1rem;
    text-align: center;
    box-shadow: 0 2px 0.1rem #638fff;
    background: linear-gradient(to right, #609fff 0%, #3367ec 100%);
    &:active {
      opacity: 0.9;
    }
  }
}
</style>
