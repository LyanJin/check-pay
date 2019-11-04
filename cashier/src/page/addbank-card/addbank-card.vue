<template>
  <main class="main">
    <div class="bg"></div>
    <header-top headTitle="添加银行卡"> </header-top>
    <section class="banklist">
      <p class="border-bottom">请绑定持卡人本人的银行卡</p>
      <ul class="addBank">
        <li class="border-bottom" v-if="$route.params.userName">
          <van-field
            label="持卡人"
            label-width="1.2rem"
            v-model="name"
            maxlength="15"
            placeholder="首次绑卡成功后只能绑定同名银行卡"
            readonly
          />
        </li>
        <li class="border-bottom" v-else>
          <van-field
            label="持卡人"
            label-width="1.2rem"
            v-model="name"
            clearable
            maxlength="15"
            placeholder="请输入姓名"
          />
        </li>
        <li class="border-bottom">
          <van-field
            label="卡号"
            label-width="1.2rem"
            v-model="bankNumber"
            clearable
            maxlength="24"
            placeholder="请输入开户名和填写的姓名一致的卡号"
          />
        </li>
      </ul>
      <footer>
        <button
          class="publicButton"
          :class="{ isdisabled: isdisabled }"
          :disabled="isdisabled"
          @click="next"
        >
          下一步
        </button>
      </footer>
    </section>
  </main>
</template>

<script>
import headerTop from '../../components/head';
import { banklocationGet } from '@/api/getData'
import { mapState, mapMutations } from 'vuex'

export default {
  data () {
    return {
      name: null,
      bankNumber: null,
      isdisabled: true, // 是否禁用输入账号按钮
    }
  },
  activated () {
    // 判断是否输入支付密码，没有返回上一页
    if (!this.$route.params.pass) {
      this.$router.go(-1)
    }
    // 判断用户名是否存在
    if (this.$route.params.userName) {
      this.name = this.$route.params.userName
    }
  },
  components: {
    headerTop
  },
  methods: {
    ...mapMutations([
      'KEYBOARD'
    ]),
    async next () {
      let params = {
        card_id: this.bankNumber ? this.bankNumber.replace(/\s+/g, "") : null
      }
      const res = await banklocationGet(params)
      if (res) {
        res.data.payment_password = this.$route.params.pass
        res.data.account_name = this.name
        res.data.card_no = this.bankNumber
        this.$router.push({ name: 'bankInformation', params: { bankInfo: res.data } })
      }

    }
  },
  computed: {
    ...mapState([
      'keyboard'
    ])
  },
  watch: {
    name: function () {
      // 禁用除.以外的特殊符号和数字  警用空格加上.replace(/\s/, '')
      this.name = this.name.replace(/[0-9=、!@#$%^&*\\{}\[\]【】~()/\|~,()`<>?"'();:。_+-]/, '')
      if (this.name && this.name.length > 0 && this.bankNumber && this.bankNumber.length > 0) {
        this.isdisabled = false
      } else {
        this.isdisabled = true
      }
    },
    bankNumber: function () {
      // 卡号每4位添加空格
      this.bankNumber = this.bankNumber.replace(/\D/g, '').replace(/(....)(?=.)/g, '$1 ')
      if (this.name && this.name.length > 0 && this.bankNumber && this.bankNumber.length > 0) {
        this.isdisabled = false
      } else {
        this.isdisabled = true
      }
    }
  },
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
        @include wh(100%, 0.9rem);
        font-size: 0.3rem;
        .van-cell {
          font-size: 0.3rem;
        }
        label {
          display: inline-block;
          width: 14%;
          font-size: 0.3rem;
          color: #333;
          padding-right: 0.2rem;
        }
      }
    }
    footer {
      padding: 0.65rem;
      .publicButton {
        margin-top: 2.2rem;
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
  // ::-webkit-input-placeholder {
  //   color: #333;
  // }

  // /* Firefox 4-18 */
  // :-moz-placeholder {
  //   color: #333;
  // }

  // /* Firefox 19-50 */
  // ::-moz-placeholder {
  //   color: #333;
  // }

  // /* - Internet Explorer 10–11
  //  - Internet Explorer Mobile 10-11 */
  // :-ms-input-placeholder {
  //   color: #333 !important;
  // }

  // /* Edge (also supports ::-webkit-input-placeholder) */
  // ::-ms-input-placeholder {
  //   color: #333;
  // }

  // /* CSS Working Draft */
  // ::placeholder {
  //   color: #333;
  // }
}
</style>
