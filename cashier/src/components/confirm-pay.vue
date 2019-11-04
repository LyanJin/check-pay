<template>
  <main v-if="show && bankList">
    <section class="chooseBank">
      <h3 class="border-bottom">
        <i class="iconfont icon-guanbi" @click="hide"></i>
        确认付款
      </h3>
      <div class="money border-bottom"><em>￥</em>{{ money | NumFormat }}</div>
      <ul>
        
        <!-- <li v-show="showQRCode" id="code">
          <div>请保存二维码,前往云闪付App扫码付款</div>
          <canvas id="canvas" v-show="!url"></canvas>
          <img class="qrcode" v-show="url" :src="url" alt="" />
        </li> -->
        <li
          class="border-bottom"
           v-for="(item, index) in bankList"
          :class="{ active: activeClass == index,disable:item.limit_min>money||item.limit_max<money }"
          :key="index"
          @click="getItem(item,index)"
        >
           
          <div class="imgs">
            <img v-if="item.value == 10||item.value == 80" src="../assets/icon/zfb.png" alt="" />
            <img v-if="item.value == 20 ||item.value == 70" src="../assets/icon/wx.png" alt="" />
            <img v-if="item.value == 30" src="../assets/icon/yl.png" alt="" />
            <img v-if="item.value == 40" src="../assets/icon/ysf.png" alt="" />
            <img v-if="item.value == 50" src="../assets/icon/yhk.png" alt="" />
          </div>

          <div class="content">
              <span>{{ item.desc }}</span>
              <em v-if="item.channel_prompt" class="prompt">{{item.channel_prompt}}</em>
              </br><span class="prompt2">
                单笔金额最低{{ item.limit_min }}最高{{ item.limit_max }}
              </span>
          </div>

          <i class="iconfont icon-gou"></i>
        </li>
        
      </ul>
      <button class="publicButton" @click="submit">确认付款</button>
    </section>
  </main>
</template>

<script>
import { depositOrderCreate } from '@/api/getData'
import { mapMutations } from 'vuex'
// import QRCode from 'qrcode'

export default {
  props: {
    money: 0,
    bankList: null,
    activeClass: 0,  //默认选择支付方式
    show: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {}
  },
  components: {
    // QRCode: QRCode
  },
  methods: {
    ...mapMutations([
      'SHOWLOADING', 'HIDELOADING'
    ]),
    hide () {
      this.$emit('hide')
    },
    // 点击切换支付方式
    getItem (item, index) {
      if (this.activeClass != index && item.limit_min <= this.money && item.limit_max >= this.money) {
        this.$emit('activeClass', index)// 把当前点击元素的index，赋值给activeClass
      }
    },
    // 提交订单
    async submit () {
      let params = {
        payment_type: this.bankList[this.activeClass].value,
        amount: String(this.money),
        channel_id: this.bankList[this.activeClass].channel_id
      }
      this.SHOWLOADING()
      const res = await depositOrderCreate(params)
      if (res && res.data.redirect_url) {
        window.location.href = res.data.redirect_url
        this.$emit('hide')
      }
    }
  },
  // 离开页面时调用
  deactivated () {
    this.HIDELOADING()
  }

}

</script>

<style lang="scss" scoped>
@import "../style/mixin";

main {
  .chooseBank {
    background: #fff;
    width: 100%;
    margin-bottom: 16px;
    h3.border-bottom {
      @include wh(100%, 0.84rem);
      line-height: 0.84rem;
      text-align: center;
      font-size: 0.34rem;
      i {
        @include wh(1rem, 0.84rem);
        position: absolute;
        left: 0;
        top: 0;
        color: #ccc;
        font-size: 0.36rem;
      }
      &::after {
        border-color: #f0f0f0;
      }
    }
    .money {
      em {
        font-size: 0.5rem;
        vertical-align: top;
      }
      text-align: center;
      font-size: 0.8rem;
      height: 1.6rem;
      line-height: 1.6rem;
    }
    ul {
      max-height: 6rem;
      overflow-x: hidden;
      overflow-y: scroll;
      // 不现实滚动条
      &::-webkit-scrollbar {
        display: none;
      }
      li {
        position: relative;
        font-size: 0.3rem;
        padding: 0 0.4rem;
        &.border-bottom {
          &::after {
            border-color: #ddd;
          }
        }

        &.disable {
          opacity: 0.4;
        }
        img {
          @include ct();
          @include wh(0.5rem, 0.5rem);
          padding-right: 0.2rem;
        }

        .content {
          display: inline-block;
          width: 86%;
          padding: 0.16rem 0;
          margin-left: 11%;
          // line-height: 0.34rem;
          .prompt {
            font-size: 0.26rem;
            width: 65%;
            text-align: right;
            float: right;
            margin-right: 0.3rem;
            margin-top: 2px;
          }
          .prompt2 {
            color: #666;
            font-size: 0.26rem;
            display: inline-block;
          }
        }

        i {
          @include ct();
          color: #609fff;
          opacity: 0;
        }
        &.active {
          i {
            opacity: 1;
          }
        }
      }
    }
    .publicButton {
      margin: 0.4rem 0.36rem;
      @include wh(90%, 0.8rem);
    }
  }
}
</style>
