<template>
  <main class="main">
    <header-top headTitle="银行卡">
      <span slot="add" class="add iconfont icon-add" @click="addBank"></span>
    </header-top>
    <section class="banklist" v-if="bankList">
      <ul v-if="bankList.length > 0">
        <li
          class="bank"
          v-for="(item, index) in bankList"
          :key="index"
          @click="adminBank(item)"
          :class="{
            red: ['1', '2', '5', '10', '11', '14'].indexOf(item.bank_idx) != -1,
            blue: ['4', '7', '13', '15'].indexOf(item.bank_idx) != -1,
            green: ['3', '6', '8'].indexOf(item.bank_idx) != -1,
            huang: ['9', '12'].indexOf(item.bank_idx) != -1
          }"
        >
          <div class="bankbg">
            <div class="bankimg">
              <img v-if="item.bank_idx == 1" src="../../assets/bank/BOC.png" />
              <img v-if="item.bank_idx == 2" src="../../assets/bank/ICBC.png" />
              <img v-if="item.bank_idx == 3" src="../../assets/bank/PSBC.png" />
              <img v-if="item.bank_idx == 5" src="../../assets/bank/CMB.png" />
              <img v-if="item.bank_idx == 4" src="../../assets/bank/CCB.png" />
              <img v-if="item.bank_idx == 6" src="../../assets/bank/ABC.png" />
              <img v-if="item.bank_idx == 7" src="../../assets/bank/SPDB.png" />
              <img v-if="item.bank_idx == 8" src="../../assets/bank/CMBC.png" />
              <img v-if="item.bank_idx == 9" src="../../assets/bank/pa.png" />
              <img v-if="item.bank_idx == 10" src="../../assets/bank/HB.png" />
              <img
                v-if="item.bank_idx == 11"
                src="../../assets/bank/CITIC.png"
              />
              <img v-if="item.bank_idx == 12" src="../../assets/bank/CEB.png" />
              <img v-if="item.bank_idx == 13" src="../../assets/bank/CIB.png" />
              <img v-if="item.bank_idx == 14" src="../../assets/bank/GDB.png" />
              <img v-if="item.bank_idx == 15" src="../../assets/bank/BCM.png" />
            </div>
            <div>
              <p class="name ellipsis">{{ item.bank_name }}</p>
              <p class="ellipsis">{{ item.card_no }}</p>
            </div>
          </div>
        </li>
      </ul>
      <div class="noBank" v-else>
        <img src="../../assets/image/noBank.png" alt="" />
        <p>
          您还未添加任何银行卡
        </p>
      </div>
    </section>

    <!-- 输入支付密码 -->
    <van-popup v-model="payPassword" position="bottom" :overlay="true">
      <pay-password
        :show="true"
        @successPassword="addBankpage"
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
import { bankcardList, PaymentPasswordCheck } from '@/api/getData'
import { Popup } from 'vant';
import payPassword from '../../components/pay-password'
import { mapState } from 'vuex'
import md5 from 'js-md5';

export default {
  name: "bankCard",
  data () {
    return {
      bankList: null,
      payPassword: false,//输入支付密码
    }
  },
  async beforeCreate () {
    const data = await bankcardList()
    if (data) {
      this.bankList = data.data.bankcards
    }
  },
  components: {
    headerTop,
    [Popup.name]: Popup,
    payPassword
  },
  methods: {
    // 支付密码正确跳转添加银行卡
    async addBankpage () {
      console.warn(111)
      this.$router.push({
        name: 'addBankCard',
        params: {
          pass: md5(this.keyboard),
          userName: this.bankList.length > 0 ? this.bankList[0].account_name : null
        }
      })
    },
    // 查看银行卡详情
    adminBank (data) {
      this.$router.push({ name: 'bankAdmin', params: { data: data, length: this.bankList.length } })
    },
    // 添加银行卡
    addBank () {
      if (this.bankList.length < 8) {
        this.payPassword = !this.payPassword;
      } else {
        this.$toast('银行卡已达上限！');
      }

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
  .add {
    float: right;
    width: 0.8rem;
    height: 0.92rem;
    font-size: 0.68rem;
    color: #fff;
    line-height: 0.92rem;
    text-align: center;
  }
  .banklist {
    ul {
      margin-top: 0.3rem;
      .red {
        background: url("../../assets/bank/red.png");
        background-size: 100% 100%;
      }
      .blue {
        background: url("../../assets/bank/blue.png");
        background-size: 100% 100%;
      }
      .green {
        background: url("../../assets/bank/green.png");
        background-size: 100% 100%;
      }
      .huang {
        background: url("../../assets/bank/huang.png");
        background-size: 100% 100%;
      }
      .bank {
        div {
          display: inline-block;
        }
        .bankbg {
          padding: 0.4rem 0.6rem;
          height: 2.4rem;
          .bankimg {
            background: #fff;
            border-radius: 100%;
            position: relative;
            @include wh(1rem, 1rem);
            margin-right: 0.2rem;
            img {
              @include wh(0.6rem, 0rrem);
              @include center();
            }
          }
          p {
            font-size: 0.4rem;
            color: #fff;
            &.name {
              color: #fff;
            }
          }
        }
      }
    }
    .noBank {
      @include cl();
      margin-top: 30%;
      text-align: center;
      img {
        width: 2rem;
      }
      p {
        color: #bbb;
        font-size: 0.28rem;
        margin-top: 0.4rem;
      }
    }
  }
}
</style>
