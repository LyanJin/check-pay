import Vue from 'vue'
import App from './App'
import router from './router'
import store from './store'
import './config/rem'
import {
  Field,
  Toast,
  Loading,
  Dialog
} from 'vant';
import Vuex from 'vuex'



Vue.use(Vuex).use(Field).use(Toast).use(Loading).use(Dialog);

// 禁止双指放大 
document.documentElement.addEventListener('touchstart', function (event) {
  if (event.touches.length > 1) {
    event.preventDefault();
  }
}, false);

// 禁止双击放大
let lastTouchEnd = 0;
document.documentElement.addEventListener('touchend', function (event) {
  let now = Date.now();
  if (now - lastTouchEnd <= 300) {
    event.preventDefault();
  }
  lastTouchEnd = now;
}, false);

// 设置为 false 以阻止 vue 在启动时生成生产提示。
Vue.config.productionTip = false


/**
 * ----------------------注册全局自定义指令---------------------
 * @author  Lyle
 */

// 只允许输入数字
Vue.directive('numberOnly', {
  componentUpdated: function (el) {
    el.value = el.value.replace(/[^\d]/g, '')
  }
})

// 不允许输入表情包与空格
Vue.directive('NoEmoji', {
  componentUpdated: function (el) {
    el.value = el.value.replace(/\s+/g, "").replace(/[^\u0020-\u007E\u00A0-\u00BE\u2E80-\uA4CF\uF900-\uFAFF\uFE30-\uFE4F\uFF00-\uFFEF\u0080-\u009F\u2000-\u201f\u2026\u2022\u20ac\r\n]/g, '')
  }
})

// 只允许输入金额保留两位小数
Vue.directive('price', {
  componentUpdated: function (el) {
    let sNum = el.value.toString(); //先转换成字符串类型
    if (sNum.indexOf('.') == 0) { //第一位就是 .
      sNum = '0' + sNum
    }
    sNum = sNum.replace(/[^\d.]/g, ""); //清除“数字”和“.”以外的字符
    sNum = sNum.replace(/\.{2,}/g, "."); //只保留第一个. 清除多余的
    sNum = sNum.replace(".", "$#$").replace(/\./g, "").replace("$#$", ".");
    sNum = sNum.replace(/^(\-)*(\d+)\.(\d\d).*$/, '$1$2.$3'); //只能输入两个小数
    //以上已经过滤，此处控制的是如果没有小数点，首位不能为类似于 01、02的金额
    if (sNum.indexOf(".") < 0 && sNum != "") {
      sNum = parseFloat(sNum);
    }
    el.value = sNum
  }
})


/**
 * --------------------注册全局自定义过滤器----------------------
 * @author  Lyle
 * 价格添加保留2小数
 */
Vue.filter('NumFormat', function (money) {
  if (money && money != null) {
    money = String(Math.abs(money));
    var left = money.split('.')[0],
      right = money.split('.')[1];
    right = right ? (right.length >= 2 ? '.' + right.substr(0, 2) : '.' + right + '0') : '.00';
    var temp = left.split('').reverse().join('').match(/(\d{1,3})/g);
    return (Number(money) < 0 ? '-' : '') + temp.join(',').split('').reverse().join('') + right;
  } else if (money === 0) { // 注意===在这里的使用，如果传入的money为0,if中会将其判定为boolean类型，故而要另外做===判断
    return '0.00';
  } else {
    return '';
  }
})

/**
 * --------------------------------路由发生变化修改页面title----------------------
 * @author  Lyle
 */
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
  next()
})


/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  render: h => h(App),
  // 预渲染执行
  // mounted() {
  //   document.dispatchEvent(new Event('custom-render-trigger'))
  // }
})
