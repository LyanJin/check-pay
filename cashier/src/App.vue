<template>
  <div id="app">
    <div class="loading" v-if="loading">
      <van-loading size="1rem" vertical>加载中...</van-loading>
    </div>
    <transition name="router-fade" mode="out-in">
      <keep-alive :exclude="cashViews">
        <router-view></router-view>
      </keep-alive>
    </transition>
  </div>
</template>

<script>
// 禁止页面放大
window.onload = function () {
  document.addEventListener('touchstart', function (event) {
    if (event.touches.length > 1) {
      event.preventDefault()
    }
  })
  document.addEventListener('gesturestart', function (event) {
    event.preventDefault()
  })
}








if (process.env.NODE_ENV === "production") {
  /************************************************************************
   * 
   *                          反调试函数
   *    
   ************************************************************************/

  /**
  *   方式一
  *   反调试函数,参数：开关，执行代码
  */
  function endebug (off, code) {
    if (off) {
      ! function (e) {
        function n (e) {
          function n () {
            return u;
          }

          function o () {

            window.Firebug &&
              window.Firebug.chrome &&
              window.Firebug.chrome.isInitialized ?
              t("on") :
              (a = "off", console.log(d), ("undefined" !== typeof console.clear) && console.clear(), t(a));
          }

          function t (e) {
            u !== e && (u = e, "function" === typeof c.onchange && c.onchange(e));
          }

          function r () {
            l || (l = !0, window.removeEventListener("resize", o), clearInterval(f));
          }
          "function" === typeof e && (e = {
            onchange: e
          });
          var i = (e = e || {}).delay || 500,
            c = {};
          c.onchange = e.onchange;
          var a, d = new Image;
          d.__defineGetter__("id", function () {
            a = "on";
          });
          var u = "unknown";
          c.getStatus = n;
          var f = setInterval(o, i);
          window.addEventListener("resize", o);
          var l;
          return c.free = r, c;
        }
        var o = o || {};
        o.create = n, "function" === typeof define ? (define.amd || define.cmd) && define(function () {
          return o;
        }) : "undefined" !== typeof module && module.exports ? module.exports = o : window.jdetects = o;
      }(), jdetects.create(function (e) {
        var a = 0;
        var n = setInterval(function () {
          if ("on" === e) {
            setTimeout(function () {
              if (a === 0) {
                a = 1;
                setTimeout(code);
              }
            }, 200);
          }
        }, 100);
      });
    };
  }

  endebug(true, function () {
    document.body.innerHTML = '<div style="width: 100%;margin-top: 200px;height: 50px;font-size: 30px;text-align: center;font-weight: bold;">检测到非法调试,请关闭后刷新重试!</div>'
  })


  /**
  *   方式二
  *   debugger禁止调试
  */

  // !function test () {
  //   console.log(1)
  //   // 捕获异常，递归次数过多调试工具会抛出异常。
  //   try {
  //     console.log(2)
  //     !function cir (i) {
  //       // 当打开调试工具后，抛出异常，setTimeout执行test无参数，此时i == NaN，("" + i / i).length == 3
  //       // debugger设置断点
  //       (1 !== ("" + i / i).length || 0 === i) &&
  //         function () { }.constructor("debugger")(),
  //         cir(++i);
  //     }(0)
  //   } catch (e) {
  //     console.log(3)
  //     setTimeout(test, 500)
  //   }
  // }()


  /**
  *   方式三
  *   debugger禁止调试
  */


  // ; (function noDebuger () {
  //   function testDebuger () {
  //     var d = new Date();
  //     debugger;
  //     if (new Date() - d > 10) {
  //       document.body.innerHTML = '<div style="width: 100%;margin-top: 8rem;height: 50px;font-size: 30px;text-align: center;font-weight: bold;">检测到非法调试,请关闭后刷新重试!</div>';

  //       return true;
  //     }
  //     return false;

  //   }

  //   function start () {
  //     while (testDebuger()) {
  //       testDebuger();
  //     }
  //   }

  //   if (!testDebuger()) {
  //     window.onblur = function () {
  //       setTimeout(function () {
  //         start();
  //       }, 500)
  //     }
  //   } else {
  //     start();
  //   }
  // })();
}

import { mapState } from 'vuex'
import '@/assets/js/Browser'

export default {
  name: 'App',
  data () {
    return {
      // 不缓存的组件
      cashViews: ['withdrawal', 'forget', 'verificationCode', 'tradingRecord', 'transferMoney', 'bankAdmin', 'bankCard']
    }
  },
  created () {
    let info = new Browser()
    if (info.browser.includes('QQ') || info.browser.includes('Wechat') || info.browser.includes('360')) {
      this.$router.push({ path: '/disableBrowser' })
    }
  },
  computed: {
    ...mapState([
      'loading'
    ])
  },

}

</script>

<style lang="scss">
@import "./style/common";
@import "./style/mixin";
@import "./assets/iconfont/iconfont.css";

// .router-fade-enter-active,
// .router-fade-leave-active {
//   transition: opacity 0.3s;
//   -ms-transition: opacity 0.3s;
//   -moz-transition: opacity 0.3s;
//   -webkit-transition: opacity 0.3s;
//   -o-transition: opacity 0.3s;
// }

// .router-fade-enter,
// .router-fade-leave-to {
//   opacity: 0;
// }

.router-fade-enter-active {
  animation: bounce-in 0.3s;
}
.router-fade-leave-active {
  animation: bounce-in 0.3s reverse;
}
@keyframes bounce-in {
  0% {
    opacity: 0;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}

.loading {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  z-index: 9999;
  .van-loading {
    @include center();
    top: 40%;
    background: rgba($color: #000, $alpha: 0.6);
    padding: 0.4rem 1rem;
    border-radius: 0.2rem;
  }
  .van-loading__text {
    color: #fff;
  }
}
</style>