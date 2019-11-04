<template>
  <main v-if="show">
    <div class="bg" @click="hide()"></div>
    <section class="choose">
      <ul>
        <li
          class="border-1"
          :class="{ active: activeClass == item.value }"
          v-for="item in List"
          :key="item.value"
          @click="getItem(item.value)"
        >
          {{ item.item }}
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
    }
  },
  data () {
    return {
      activeClass: 0,  //默认选择支付宝
      List: [
        { item: '全部', value: 0 },
        { item: '充值', value: 1 },
        { item: '提现', value: 2 },
        { item: '提现退回', value: 3 },
        { item: '转账', value: 5 },
        { item: '系统调整', value: 6 }
      ]
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
      this.$emit('getItem', this.activeClass)
    }
  },

}

</script>

<style lang="scss" scoped>
@import "../style/mixin";

main {
  .bg {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    z-index: 10;
    background: rgba(#000, 0.4);
  }
  .choose {
    position: fixed;
    top: 0.92rem;
    left: 0;
    background: #fff;
    z-index: 11;
    width: 100%;
    ul {
      text-align: center;
      li {
        display: inline-block;
        @include wh(1.8rem, 0.8rem);
        line-height: 0.8rem;
        margin: 0.3rem;
        font-size: 0.32rem;
        &::after {
          border-radius: 0.1rem;
        }
        &.active {
          color: #609fff;
          background: #eef5ff;
          &::after {
            border-color: #609fff;
          }
        }
      }
    }
  }
}
</style>
