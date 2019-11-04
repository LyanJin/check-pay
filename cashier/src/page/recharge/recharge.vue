<template>
  <main class="main">
    <header-top headTitle="充值"></header-top>
    <section v-if="limit_min > 0">
      <h4>单笔充值金额最低{{ limit_min }}元起，最高{{ limit_max }}元</h4>
      <ul class="clear">
        <li>
          充值金额
        </li>
        <li class="money border-bottom">
          <input
            v-NoEmoji
            class=""
            type="tel"
            placeholder="请输入充值金额"
            maxlength="8"
            v-price
            v-model.trim="money"
            @keydown.space.prevent
          />
        </li>
        <li>
          <button
            class="publicButton" 
            @click="next"
            :class="{ isdisabled: isdisabled }"
            :disabled="isdisabled"
          >
            立即充值
          </button>
        </li>
      </ul>
    </section>

    <van-popup v-model="show" position="bottom">
      <confirm-pay
        :show="true"
        :money="money"
        :bankList="bankList"
        :activeClass="activeClass"
        @activeClass="activeNumber"
        @hide="
          () => {
            show = false;
          }
        "
      ></confirm-pay>
    </van-popup>
  </main>
</template>

<script>

import headerTop from '../../components/head'
import confirmPay from '../../components/confirm-pay'
import { Popup } from 'vant';
import { limitConfigGet, paymentTypeList } from '@/api/getData'
import { removeStore } from '@/config/common'

export default {
  data () {
    return {
      money: null,
      bankList: [],
      limit_min: 0,
      limit_max: 0,
      isdisabled: true, // 是否禁用充值按钮
      activeClass: 0,  //默认选择支付方式
      show: false  //弹出确认付款
    }
  },
  async activated () {
    if (this.limit_min == 0) {
      const limit = await limitConfigGet()
      if (limit) {
        this.limit_min = limit.data.limit_min
        this.limit_max = limit.data.limit_max
      }
    }
  },
  components: {
    headerTop,
    confirmPay,
    [Popup.name]: Popup
  },
  methods: {
    userDelete () {
      this.phoneNumber = null
    },
    async next () {
      // 通过金额判断可用的充值渠道列表
      const data = await paymentTypeList({ amount: this.money })
      if (data) {
        this.bankList = data.data.payment_type_list
        this.show = !this.show

        // 默认选择支付方式
        for (let i = 0; i < this.bankList.length; i++) {
          if (this.bankList[i].limit_min <= this.money && this.bankList[i].limit_max >= this.money) {
            this.activeClass = i
            return
          }
        }
      }
    },
    // 是否显示密码
    changePassWordType () {
      this.showPassword = !this.showPassword
    },
    activeNumber (data) {
      console.warn(data)
      this.activeClass = data
    }
  },
  watch: {
    money: function () {
      if (this.money > 0 && this.money >= Number(this.limit_min) && this.money <= Number(this.limit_max)) {
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
    margin-top: 1.6rem;
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
