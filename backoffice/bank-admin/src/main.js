import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store/index'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'

Vue.use(ElementUI)

Vue.config.productionTip = false

/**
 * ----------------------注册全局自定义指令---------------------
 * @author  Lyle
 */

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
    sNum = sNum.replace(/^(-)*(\d+)\.(\d\d).*$/, '$1$2.$3'); //只能输入两个小数
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
    money = String(money);
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

Vue.filter('merchantType', function (type) {
  if (type == 'TEST') {
    return '测试商户'
  } else {
    return '普通商户'
  }
})

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')