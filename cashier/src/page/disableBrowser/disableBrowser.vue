<template>
  <main class="main">
    <div class="nothing">
      <img src="../../assets/icon/404.png" alt="">
    </div>
    <h1>很抱歉我们不支持当前您使用的浏览器</h1>

    <h3>为了保证体验，请使用推荐的浏览器访问！</br>
    给您带来不便，还请谅解！
    </h3>

    <div class="browser">
      推荐浏览器
      <section>
        <a :href="gugourl">
         <img src="../../assets/icon/gugo.jpeg" alt="">
            <p>下载谷歌浏览器</p>
        </a>

        <a :href="ucurl">
            <img src="../../assets/icon/uc.jpeg" alt="">
            <p>下载UC浏览器</p>
        </a>
           

        <a v-if="ios">
          <img src="../../assets/icon/pg.jpeg" alt="">
          <p>Safari浏览器</p>
        </a>
      </section>
    </div>
  </main>
</template>

<script>

export default {
  data () {
    return {
      ios: false,
      gugourl: 'https://www.google.com/intl/zh-CN/chrome/',
      ucurl: 'https://wap.uc.cn',
    }
  },
  activated () {
    if (navigator.userAgent.match(/iphone|ipad|ipod/i)) {
      this.ios = true
    } else {
      this.ios = false

    }
  },
  components: {
  },
  methods: {


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
  text-align: center;
  background: #fff;
  .nothing {
    width: 70%;
    display: inline-block;
    margin-bottom: 0.3rem;
    img {
      width: 100%;
    }
  }
  h1 {
    margin-bottom: 0.4rem;
    font-size: 0.4rem;
  }
  h3 {
    color: #333;
  }
  .browser {
    font-size: 0.4rem;
    margin-top: 0.4rem;
    section {
      margin-top: 0.4rem;
      a {
        width: 25%;
        display: inline-block;
        font-size: 0.26rem;
        color: #000;
        img {
          width: 70%;
        }
      }
    }
  }
}
</style>
