import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

const login = () => import('@/page/login');
const manage = () => import('@/page/manage');
const home = () => import('@/page/home');


/*******************************
            交易管理
 *******************************/
//充值订单详细
const payOrder = () => import('@/page/tradingManage/payOrder');
//提现订单查询
const withdrawalOrder = () => import('@/page/tradingManage/withdrawalOrder');



const routes = [{
    path: '/',
    name: 'login',
    component: login,
    meta: {
      title: "登录"
    },
  },
  {
    path: '/manage',
    component: manage,
    redirect: "/home",
    meta: {
      title: "首页"
    },
    children: [{
        path: '/home',
        component: home,
        meta: {
          title: "数据统计"
        },
      },

      /*********************************
       *  
       *            交易管理
       * 
       ********************************/
      {
        path: '/payOrder',
        name: 'payOrder',
        component: payOrder,
        meta: {
          title: "充值订单查询"
        },
      },
      {
        path: '/withdrawalOrder',
        name: 'withdrawalOrder',
        component: withdrawalOrder,
        meta: {
          title: "提现订单查询"
        },
      },
    ]
  }
]
// history
export default new Router({
  mode: 'hash',
  base: process.env.BASE_URL,
  routes,
})