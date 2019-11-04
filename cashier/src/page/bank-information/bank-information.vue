<template>
  <main class="main">
    <div class="bg"></div>
    <header-top headTitle="填写银行卡信息"> </header-top>
    <section class="banklist">
      <p class="border-bottom"></p>
      <ul class="addBank">
        <li class="border-bottom">
          <label>开户银行</label>
          <input type="text" v-model="bankInfo.bank_name" readonly />
        </li>

        <!-- 选择地址插件   暂不使用 -->
        <!-- <li class="border-bottom " @click="show()">
          <label for="branch">所在地区</label>
          <input v-NoEmoji type="text" v-model.trim="address" readonly />
          <span class="address right iconfont icon-enter"> </span>
        </li> -->

        <li class="border-bottom ">
          <label>所在地区</label>
          <input
            type="text"
            v-model="bankInfo.province + ' ' + bankInfo.city"
            readonly
          />
        </li>

        <li class="border-bottom">
          <label for="branch">支行名称</label>
          <input
            v-NoEmoji
            type="text"
            placeholder="选填"
            v-model.trim="branch"
            id="branch"
          />
          <span class="delete right" v-if="branch" @click="bankDelete()">
            <i></i>
          </span>
        </li>
      </ul>
      <footer>
        <button class="publicButton" @click="next">
          完成
        </button>
      </footer>
    </section>

    <van-dialog
      v-model="show"
      title="为避免提现失败，请仔细核银行卡信息"
      show-cancel-button
      confirm-button-text="确认无误"
      @confirm="addBankCard"
    >
      <ul class="dialogBank">
        <li>
          <label>持卡人</label>
          <span>{{ bankInfo.account_name }}</span>
        </li>
        <li>
          <label>银行卡号</label>
          <span>{{ bankInfo.card_no }}</span>
        </li>
        <li>
          <label>地区</label>
          <span>{{ bankInfo.province }} {{ bankInfo.city }}</span>
        </li>
        <li v-if="bankInfo.branch">
          <label>支行名称</label>
          <span>{{ bankInfo.branch }}</span>
        </li>
      </ul>
    </van-dialog>

    <!-- 选择地址插件   暂不使用 -->
    <!-- <van-popup v-model="areaShow" position="bottom" :overlay="true">
      <van-area
        :area-list="areaList"
        @confirm="onConfirm"
        @cancel="show"
        v-if="areaList"
      />
    </van-popup> -->
  </main>
</template>

<script>
import headerTop from '../../components/head';
import { Area, Popup, Dialog } from 'vant';
import { bankcardAdd } from '@/api/getData'
// import AreaData from '../../../static/area.js';

export default {
  data () {
    return {
      branch: null, //支行名称
      show: false, //显示弹窗
      bankInfo: {}
      // areaList: AreaData,   // 地址选择数据
      // areaShow: false,  //是否显示地址

    }
  },
  activated () {
    if (this.$route.params.bankInfo) {
      this.bankInfo = this.$route.params.bankInfo
      console.warn(this.bankInfo)
    } else {
      this.$router.go(-1)
    }
  },
  components: {
    headerTop,
    [Area.name]: Area,
    [Popup.name]: Popup,
    [Dialog.name]: Dialog,
  },
  methods: {
    bankDelete () {
      this.branch = null
    },
    next () {
      this.bankInfo.branch = this.branch
      this.show = !this.show
    },
    async addBankCard () {
      // 删除空格
      this.bankInfo.card_no = this.bankInfo.card_no.replace(/\s+/g, "")
      const data = await bankcardAdd(this.bankInfo)
      if (data) {
        this.$toast.success('银行卡添加成功');
        setTimeout(() => {
          this.$router.go(-1)
        }, 1500)
      }
      console.warn(data)
    }
    // show () {
    //   this.areaShow = !this.areaShow
    // },
    // onConfirm (data) {
    //   let address = ''
    //   data.forEach(element => {
    //     console.warn(element.name)
    //     address += ' ' + element.name
    //   });
    //   this.address = address
    //   this.show()
    // }

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
        label {
          display: inline-block;
          width: 18%;
          font-size: 0.3rem;
          color: #333;
          padding-right: 0.2rem;
        }
        input {
          @include wh(68%, 0.4rem);
          line-height: 0.4rem;
          background: transparent;
          font-size: 0.3rem;
        }
        .delete {
          @include wh(9%, 0.9rem);
          i {
            display: inline-block;
            @include bis("../../assets/icon/copy.png");
            @include wh(0.48rem, 0.48rem);
            margin-top: 0.2rem;
          }
        }
        .address {
          font-size: 0.6rem;
          color: #bbb;
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
  // 弹窗样式
  .dialogBank {
    padding: 0 0.6rem 0.6rem 0.6rem;
    li {
      padding-top: 0.6rem;
      font-size: 0.3rem;
      label {
        text-align: right;
        display: inline-block;
        width: 25%;
        color: #666;
        vertical-align: top;
      }
      span {
        display: inline-block;
        width: 71%;
        padding-left: 4%;
        color: #333;
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
