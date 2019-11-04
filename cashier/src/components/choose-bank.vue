<template>
  <main v-if="show">
    <section class="chooseBank" v-if="bankList">
      <h3 class="border-bottom">
        <i class="iconfont icon-guanbi" @click="hide()"></i>
        选择银行卡
      </h3>
      <ul>
        <li
          class="border-bottom"
          :class="{ active: activeClass == index }"
          v-for="(item, index) in bankList"
          :key="index"
          @click="getItem(index)"
        >
          <img v-if="item.bank_idx == 1" src="../assets/bank/BOC.png" />
          <img v-if="item.bank_idx == 2" src="../assets/bank/ICBC.png" />
          <img v-if="item.bank_idx == 3" src="../assets/bank/PSBC.png" />
          <img v-if="item.bank_idx == 5" src="../assets/bank/CMB.png" />
          <img v-if="item.bank_idx == 4" src="../assets/bank/CCB.png" />
          <img v-if="item.bank_idx == 6" src="../assets/bank/ABC.png" />
          <img v-if="item.bank_idx == 7" src="../assets/bank/SPDB.png" />
          <img v-if="item.bank_idx == 8" src="../assets/bank/CMBC.png" />
          <img v-if="item.bank_idx == 9" src="../assets/bank/pa.png" />
          <img v-if="item.bank_idx == 10" src="../assets/bank/HB.png" />
          <img v-if="item.bank_idx == 11" src="../assets/bank/CITIC.png" />
          <img v-if="item.bank_idx == 12" src="../assets/bank/CEB.png" />
          <img v-if="item.bank_idx == 13" src="../assets/bank/CIB.png" />
          <img v-if="item.bank_idx == 14" src="../assets/bank/GDB.png" />
          <img v-if="item.bank_idx == 15" src="../assets/bank/BCM.png" />
          <span>
            {{ item.bank_name }}
            ({{ item.card_no.substr(item.card_no.length - 4) }})
          </span>
          <i class="iconfont icon-gou"></i>
        </li>
        <li @click="addBank()">
          <img src="../assets/icon/add.png" />
          <span>添加新银行卡</span>
        </li>
      </ul>
    </section>
  </main>
</template>

<script>

export default {
  props: {
    show: {
      type: Boolean,
      default: false
    },
    bankList: null
  },
  data () {
    return {
      activeClass: 0,  //默认选择支付宝
      chooseBank: true, //  true 选择银行卡， false 输入支付密码

    }
  },
  computed: {

  },
  methods: {
    hide () {
      this.$emit('hide')
    },
    getItem (index) {
      this.activeClass = index;  // 把当前点击元素的index，赋值给activeClass
      this.$emit('getbank', this.bankList[this.activeClass])
    },
    addBank () {
      this.$router.push({ path: '/bankCard' })
    },
  }
}

</script>

<style lang="scss" scoped>
@import "../style/mixin";

main {
  .chooseBank {
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
    ul {
      overflow: auto;
      max-height: 6rem;
      min-height: 4rem;
      li {
        @include wh(100%, 0.96rem);
        font-size: 0.3rem;
        line-height: 0.96rem;
        padding: 0 0.4rem;
        &.border-bottom {
          &::after {
            border-color: #ddd;
          }
        }
        img {
          @include wh(0.6rem, 0.6rem);
          padding-right: 0.2rem;
          padding-top: 0.18rem;
          float: left;
        }
        i {
          float: right;
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
  }
}
</style>
