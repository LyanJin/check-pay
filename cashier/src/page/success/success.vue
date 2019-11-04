<template>
  <main class="main">
    <header-top headTitle="申请成功"></header-top>
    <section>
      <div class="header">
        <img src="../../assets/image/success.png" alt="" />
        <div>提现申请成功</div>
        <span>预计2小时内到账</span>
      </div>
      <ul class="line">
        <li class="active">
          <div>
            <span class="iconfont icon-gou"></span>
          </div>
          <span>申请成功</span>
        </li>
        <li>
          <div>
            <span class="iconfont icon-gou"></span>
          </div>
          <span>处理中</span>
        </li>
        <li>
          <div>
            <span class="iconfont icon-gou"></span>
          </div>
          <span>到账成功</span>
        </li>
      </ul>
      <footer>
        <button class="publicButton" @click="next">
          完成
        </button>
      </footer>
    </section>
  </main>
</template>

<script>
import headerTop from '../../components/head'
export default {
  data () {
    return {

    }
  },
  components: {
    headerTop
  },
  methods: {
    next () {
      this.$router.push({ path: '/home' })
    }
  }
}
</script>

<style scoped lang="scss">
@import "../../style/mixin";
.main {
  padding: 0.65rem;
  padding-top: 0.92rem;
  .header {
    padding-top: 0.8rem;
    text-align: center;
    img {
      @include wh(1.6rem, 1.6rem);
    }
    div {
      font-size: 0.36rem;
    }
    span {
      font-size: 0.24rem;
      color: #bbb;
    }
  }
  .line {
    margin-top: 0.32rem;
    li {
      width: 33%;
      float: left;
      text-align: center;
      &.active {
        div {
          span {
            background: #609fff;
            &::after {
              background: #609fff;
            }
          }
        }
      }
      div {
        span {
          display: inline-block;
          @include wh(0.36rem, 0.36rem);
          text-align: center;
          line-height: 0.36rem;
          border-radius: 100%;
          color: #fff;
          background: #ddd;
          font-size: 0.24rem;
          position: relative;
          &::after {
            content: "";
            @include wh(1.1rem, 0.04rem);
            border-radius: 0.1rem;
            background: #ddd;
            z-index: -1;
          }
        }
      }
    }
    li:nth-child(1) {
      span {
        &::after {
          left: 0.2rem;
          @include ct();
        }
      }
    }
    li:nth-child(2) {
      span {
        &::after {
          width: 2.24rem !important;
          @include center();
        }
      }
    }
    li:nth-child(3) {
      span {
        &::after {
          right: 0.2rem;
          @include ct();
        }
      }
    }
  }

  .publicButton {
    margin-top: 0.6rem;
  }
}
</style>
