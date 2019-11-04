<template>
  <main class="main">
    <header-top headTitle="转账"></header-top>
    <section class="loginForm">
      <ul class="clear">
        <li @click="show">
          {{ areaCode.cn }}
          <span class="right country"> {{ areaCode.phone_code }}</span>
        </li>
        <li>
          <input
            v-NoEmoji
            type="text"
            placeholder="请输入手机号码或账户名"
            maxlength="11"
            v-model.trim="phoneNumber"
          />
          <span class="delete right" v-if="phoneNumber" @click="userDelete()">
            <i></i>
          </span>
        </li>
      </ul>
      <button
        class="publicButton"
        @click="next"
        :class="{ isdisabled: isdisabled }"
        :disabled="isdisabled"
      >
        下一步
      </button>
    </section>
    <!-- <footer class="record">
      <div class="title border-bottom">
        最近转账
      </div>
       <ul>
        <li class="border-bottom clear">
          <div><img src="../../assets/image/default.png" alt="" /></div>
          <div>156****7865</div>
        </li>
        <li class="border-bottom clear">
          <div><img src="../../assets/image/default.png" alt="" /></div>
          <div>156****7865</div>
        </li>
        <li class="border-bottom clear">
          <div><img src="../../assets/image/default.png" alt="" /></div>
          <div>156****7865</div>
        </li>
      </ul> 
      <div class="null">
        还没有记录
      </div>
    </footer>-->
    <!-- 手机归属地 -->
    <van-popup v-model="showPhone" position="right" :overlay="false">
      <countryPhone
        :show="true"
        @hide="
          () => {
            showPhone = false;
          }
        "
      ></countryPhone>
    </van-popup>
  </main>
</template>

<script>
import headerTop from '../../components/head';
import countryPhone from '../../components/country-phone';
import { Popup } from 'vant';
import { mapState } from 'vuex'
import { getSessStore } from '@/config/common'
import { transferAccountQuery } from '@/api/getData'


export default {
  data () {
    return {
      phoneNumber: null, // 手机号
      isdisabled: true, // 是否禁用输入账号按钮
      showPhone: false, // 弹出手机归属地页
    }
  },
  activated () {
    this.phoneNumber = null
  },
  components: {
    headerTop,
    countryPhone,
    [Popup.name]: Popup
  },
  computed: {
    ...mapState([
      'areaCode'
    ])
  },
  methods: {
    userDelete () {
      this.phoneNumber = null
    },
    async next () {
      if (this.phoneNumber == getSessStore('phone').phone) {
        return this.$toast('用户不能转给自己');
      }

      const data = await transferAccountQuery({ zone: this.areaCode.phone_code, account: this.phoneNumber })
      if (data) {
        this.$router.push({
          name: 'transferMoney',
          params: {
            phone: this.phoneNumber,
            is_auth: data.data.is_auth,
            transfer_limit: data.data.transfer_limit
          }
        })
      }
    },
    show () {
      this.showPhone = !this.showPhone
    },
  },
  watch: {
    phoneNumber: function () {
      if (this.phoneNumber) {
        this.isdisabled = false
      } else {
        this.isdisabled = true
      }
      // if (this.phoneNumber && this.phoneNumber.length >= 9) {
      //   this.isdisabled = false
      // } else {
      //   this.isdisabled = true
      // }
      // if (this.phoneNumber && this.phoneNumber.length < 11 && this.areaCode.phone_code == '+86') {
      //   this.isdisabled = true
      // }
    }
  }
}
</script>

<style lang="scss" scoped>
@import "src/style/mixin";

.main {
  padding-top: 0.92rem;
  .loginForm {
    padding: 0 0.65rem;
    padding-top: 0.5rem;
    ul {
      padding-bottom: 0.6rem;
      li {
        position: relative;
        @include sc(0.3rem);
        @include wh(100%, 1.1rem);
        line-height: 1.2rem;
        border-bottom: 0.01rem solid #999;
        input {
          @include wh(90%, 0.4rem);
          line-height: 0.4rem;
          margin-top: 0.4rem;
          background: transparent;
          font-size: 0.3rem;
        }
        .country {
          height: 1rem;
          color: #888;
          padding-right: 0.6rem;
          background: url("../../assets/icon/rigth.png") no-repeat right 0.36rem;
          background-size: 50% 50%;
          font-size: 0.28rem;
        }
        .delete {
          @include wh(9%, 1rem);
          i {
            display: inline-block;
            @include bis("../../assets/icon/copy.png");
            @include wh(0.48rem, 0.48rem);
            margin-top: 0.4rem;
          }
        }
        .look {
          @include wh(9%, 1rem);
          i {
            display: inline-block;
            @include bis("../../assets/icon/eye.png");
            @include wh(0.48rem, 0.48rem);
            margin-top: 0.4rem;
          }
          .openEye {
            @include bis("../../assets/icon/eyeopen.png");
          }
        }
      }
    }
    .ward {
      color: #f85f5f;
      font-size: 0.26rem;
      margin: 0.12rem 0;
    }
    .to_forget {
      padding-top: 0.1rem;
      a {
        color: #3367ec;
        font-size: 0.26rem;
      }
    }
  }
  .record {
    background: #f6f6f6;
    margin-top: 0.7rem;
    position: relative;
    @include wh(100%, 7rem);
    .border-bottom {
      &::after {
        border-color: #ddd;
      }
    }
    .title {
      height: 0.6rem;
      line-height: 0.6rem;
      font-size: 0.28rem;
      color: #888;
      padding: 0 0.3rem;
    }
    ul {
      height: 100%;
      overflow: auto;
      li {
        padding: 0 0.3rem;
        height: 0.8rem;
        line-height: 0.8rem;
        div {
          display: inline-block;
          font-size: 0.28rem;
          color: #888;
          img {
            @include wh(0.48rem, 0.48rem);
            margin-right: 0.16rem;
            vertical-align: middle;
          }
        }
      }
    }
    .null {
      @include center();
      font-size: 0.28rem;
      color: #bbb;
    }
  }
  .van-popup--right {
    width: 100%;
  }
}
</style>
