import Vue from 'vue'
import Router from 'vue-router'
import {
  routerMode
} from '../config/env'
import {
  getSessStore,
  setSessStore
} from '@/config/common'


const home = r => require.ensure([], () => r(require('../page/home/home')), 'home')
const login = r => require.ensure([], () => r(require('../page/login/login')), 'login')
const forget = r => require.ensure([], () => r(require('../page/forget/forget')), 'forget')
// 忘记支付密码页   需要输入银行卡用户名验证暂未启用
// const forgetPay = r => require.ensure([], () => r(require('../page/forget-pay/forget-pay')), 'forgetPay')
const messageCode = r => require.ensure([], () => r(require('../page/forget-pay/messageCode')), 'forgetPay')
const verificationCode = r => require.ensure([], () => r(require('../page/verification-code/verification-code')), 'verificationCode')
const recharge = r => require.ensure([], () => r(require('../page/recharge/recharge')), 'recharge')
const withdrawal = r => require.ensure([], () => r(require('../page/withdrawal/withdrawal')), 'withdrawal')
const success = r => require.ensure([], () => r(require('../page/success/success')), 'success')
const transfer = r => require.ensure([], () => r(require('../page/transfer/transfer')), 'transfer')
const transferMoney = r => require.ensure([], () => r(require('../page/transfer-money/transfer-money')), 'transferMoney')
const bankCard = r => require.ensure([], () => r(require('../page/bank-card/bank-card')), 'bankCard')
const addBankCard = r => require.ensure([], () => r(require('../page/addbank-card/addbank-card')), 'addBankCard')
const bankInformation = r => require.ensure([], () => r(require('../page/bank-information/bank-information')), 'bankInformation')
const bankAdmin = r => require.ensure([], () => r(require('../page/bank-admin/bank-admin')), 'bankAdmin')
const tradingRecord = r => require.ensure([], () => r(require('../page/trading-record/trading-record')), 'tradingRecord')
const orderInfo = r => require.ensure([], () => r(require('../page/trading-record/orderInfo')), 'tradingRecord')
const setting = r => require.ensure([], () => r(require('../page/setting/setting')), 'setting')
const disableBrowser = r => require.ensure([], () => r(require('../page/disableBrowser/disableBrowser')), 'disableBrowser')

Vue.use(Router)

export default new Router({
  mode: routerMode,
  routes: [
    // 登录页
    {
      path: '/',
      component: login,
      meta: {
        title: "登录"
      },
      beforeEnter: (to, from, next) => {
        // 添加守卫判断是否登录
        if (getSessStore('token')) {
          next('/home')
        } else {
          next()
        }
      }
    },
    // 登录页
    {
      path: '/login',
      name: 'login',
      component: login,
      meta: {
        title: "登录"
      },
      beforeEnter: (to, from, next) => {
        // 添加守卫判断是否登录
        if (getSessStore('token')) {
          next('/home')
        } else {
          next()
        }
      }
    },
    // 首页
    {
      path: '/home',
      name: 'home',
      component: home,
      meta: {
        title: "首页"
      }
    },
    // 忘记密码页
    {
      path: '/forget',
      name: 'forget',
      component: forget,
      meta: {
        title: "找回密码"
      }
    },
    // // 忘记支付密码页
    // {
    //   path: '/forgetPay',
    //   name: 'forgetPay',
    //   component: forgetPay,
    //   meta: {
    //     title: "忘记支付密码"
    //   }
    // },
    // 验证手机号
    {
      path: '/messageCode',
      name: 'messageCode',
      component: messageCode,
      meta: {
        title: "验证手机号"
      }
    },
    // 输入验证码
    {
      path: '/verificationCode',
      name: 'verificationCode',
      component: verificationCode,
      meta: {
        title: "输入验证码"
      }
    },
    // 充值页
    {
      path: '/recharge',
      name: 'recharge',
      component: recharge,
      meta: {
        title: "充值"
      }
    },
    // 提现页
    {
      path: '/withdrawal',
      name: 'withdrawal',
      component: withdrawal,
      meta: {
        title: "提现"
      }
    },
    // 申请成功页
    {
      path: '/success',
      name: 'success',
      component: success,
      meta: {
        title: "申请成功"
      }
    },
    // 转账页
    {
      path: '/transfer',
      name: 'transfer',
      component: transfer,
      meta: {
        title: "转账"
      }
    },
    // 转账金额页
    {
      path: '/transferMoney',
      name: 'transferMoney',
      component: transferMoney,
      meta: {
        title: "转账"
      }
    },
    // 银行卡
    {
      path: '/bankCard',
      name: 'bankCard',
      component: bankCard,
      meta: {
        title: "银行卡"
      }
    },
    // 添加银行卡
    {
      path: '/addBankCard',
      name: 'addBankCard',
      component: addBankCard,
      meta: {
        title: "银行卡"
      }
    },
    // 填写银行卡信息页
    {
      path: '/bankInformation',
      name: 'bankInformation',
      component: bankInformation,
      meta: {
        title: "填写银行卡信息"
      }
    },
    // 银行卡管理页
    {
      path: '/bankAdmin',
      name: 'bankAdmin',
      component: bankAdmin,
      meta: {
        title: "填写银行卡信息"
      }
    },
    // 交易记录页
    {
      path: '/tradingRecord',
      name: 'tradingRecord',
      component: tradingRecord,
      meta: {
        title: '交易记录'
      }
    },
    // 订单详情
    {
      path: '/orderInfo',
      name: 'orderInfo',
      component: orderInfo,
      meta: {
        title: '交易详情'
      }
    },
    // 设置页
    {
      path: '/setting',
      name: 'setting',
      component: setting,
      meta: {
        title: '设置'
      }
    },
    //  浏览器提示
    {
      path: '/disableBrowser',
      name: 'disableBrowser',
      component: disableBrowser,
      meta: {
        title: '设置'
      }
    },
  ]
})
