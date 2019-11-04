<template>
  <header id="head_top">
    <!-- 自定义返回事件 -->
    <slot
      name="head"
      v-if="component"
    ></slot>
    <!-- 默认返回 -->
    <section
      class="head_goback iconfont icon-return"
      @click="$router.go(-1)"
      v-else
    ></section>
    <section class="title_head ellipsis" v-if="headTitle">
      <span class="title_text">{{ headTitle }}</span>
    </section>
    <slot name="add"></slot>
    <slot name="screening"></slot>
  </header>
</template>

<script>
export default {
  data () {
    return {

    }
  },
  mounted () {

  },
  props: {
    headTitle: {
      type: String,
      default: null
    },
    component: {
      type: Boolean,
      default: false
    }
  },
  computed: {

  },
  methods: {

  },

}

</script>

<style lang="scss" scoped>
@import "../style/mixin";

#head_top {
   background: linear-gradient(to right, #609FFF 0%, #3367EC 100%);
  position: fixed;
  z-index: 100;
  left: 0;
  top: 0;
  @include wh(100%, 0.92rem);
}
.head_goback {
  float: left;
  width: 0.8rem;
  height: 0.92rem;
  font-size: 0.68rem;
  color: #fff;
  line-height: 0.92rem;
  text-align: center;
}
.head_login {
  right: 0.55rem;
  @include sc(0.65rem, #fff);
  @include ct;
  .login_span {
    color: #fff;
  }
  .user_avatar {
    fill: #fff;
    @include wh(0.8rem, 0.8rem);
  }
}
.title_head {
  @include center;
  width: 50%;
  color: #fff;
  text-align: center;
  .title_text {
    @include sc(0.37rem, #fff);
    text-align: center;
    font-weight: bold;
  }
}
</style>
