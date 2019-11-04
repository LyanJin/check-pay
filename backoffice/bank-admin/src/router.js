import Vue from 'vue'
import Router from 'vue-router'
import {
  getSessStore
} from '@/config/mUtils'

Vue.use(Router)

const login = () => import('@/page/login');
const manage = () => import('@/page/manage');
const home = () => import('@/page/home');


/*************************************
 *              系统管理
 ************************************/
//充值订单详细
// const payOrder = r => require.ensure([], () => r(require('../page/tradingManage/payOrder')), 'payOrder');
//出款银行卡列表
const bankCardList = () => import('@/page/systemManage/bankCardList');



/*******************************
            交易管理
 *******************************/
//交易管理
const tradeManage = () => import('@/page/tradingManage/tradeManage');
//充值订单详细
const payOrder = () => import('@/page/tradingManage/payOrder');
//订单详细
const orderDetails = () => import('@/page/tradingManage/orderDetails');
//人工补单
const fillOrder = () => import('@/page/tradingManage/fillOrder');
//提现订单详细
const withdrawalOrder = () => import('@/page/tradingManage/withdrawalOrder');
//提现订单审核
const withdrawalAudit = () => import('@/page/tradingManage/withdrawalAudit');
//人工出款
const artificialOutMoney = () => import('@/page/tradingManage/artificialOutMoney');

/****************************************
            资金明细管理
*****************************************/
//用户资金明细管理
const userFundsDetail = () => import('@/page/fundsDetail/userFundsDetail');
//商家资金明细管理
const merchantFundsDetail = () => import('@/page/fundsDetail/merchantFundsDetail');

/*************************************
 *            商户管理
 ************************************/
//商户管理
const merchantManage = () => import('@/page/merchantManage/merchantManage');
//商家列表
const merchantlist = () => import('@/page/merchantManage/merchantList');
//新建商家
const newMerchant = () => import('@/page/merchantManage/newMerchant');
//商家详情
const merchantDetails = () => import('@/page/merchantManage/merchantDetails');
//编辑商家
const editorMerchant = () => import('@/page/merchantManage/editorMerchant');
//余额调整
const balanceEditor = () => import('@/page/merchantManage/balanceEditor');





/*************************************
 *            用户管理
 ************************************/
//用户管理
const userManage = () => import('@/page/userManage/userManage');
//用户列表
const userList = () => import('@/page/userManage/userList');
//用户余额调整
const userBalanceEditor = () => import('@/page/userManage/userBalanceEditor');
//用户详情
const userDetails = () => import('@/page/userManage/userDetails');







/*************************************
 *            通道管理
 ************************************/

//通道管理
const channelManage = () => import('@/page/channelManage/channelManage');
//充值通道列表
const rechargeableChannelList = () => import('@/page/channelManage/rechargeableChannelList');
//新建与编辑充值通道
const newRechargeableChannel = () => import('@/page/channelManage/newRechargeableChannel');
//代付通道列表
const insteadChannelList = () => import('@/page/channelManage/insteadChannelList');
//新建与编辑代付通道
const newInsteadChannel = () => import('@/page/channelManage/newInsteadChannel');
//引导规则
const guideRuleList = () => import('@/page/channelManage/guideRuleList');
//新建与编辑引导规则
const newGuideRule = () => import('@/page/channelManage/newGuideRule');







/*******************************
            系统管理
 *******************************/
//系统管理
const systemManage = () => import('@/page/systemManage/systemManage');
//修改密码
const ChangePassword = () => import('./page/systemManage/ChangePassword');
//账号管理
// const accountManage = () => import('@/page/accessManage/accountManage');








const routes = [{
    path: '/',
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

      //系统管理
      {
        path: '/bankCardList',
        name: 'bankCardList',
        component: bankCardList,
        meta: {
          title: "出款银行卡列表"
        }
      },


      // //权限管理
      // {
      //   path: '/accountManage',
      //   name: 'accountManage',
      //   component: accountManage,
      //   meta: {
      //     title: "账户管理"
      //   }
      // },
  



      // 资金明细管理
      {
        path: '/userFundsDetail',
        name: 'userFundsDetail',
        component: userFundsDetail,
        meta: {
          title: "用户资金明显"
        }
      },
      {
        path: '/merchantFundsDetail',
        name: 'merchantFundsDetail',
        component: merchantFundsDetail,
        meta: {
          title: "商家资金明显"
        }
      },




      /*********************************
       *  
       *            交易管理
       * 
       ********************************/
      {
        path: '/tradeManage',
        name: 'tradeManage',
        redirect: '/payOrder',
        component: tradeManage,
        meta: {
          title: "交易管理"
        },
        children: [{
            path: '/payOrder',
            name: 'payOrder',
            component: payOrder,
            meta: {
              title: "充值订单查询"
            },
            children: [{
                path: '/orderDetails',
                name: 'orderDetails',
                component: orderDetails,
                meta: {
                  title: "充值订单详情"
                }
              },
              {
                path: '/fillOrder',
                name: 'fillOrder',
                component: fillOrder,
                meta: {
                  title: "人工补单"
                }
              },
            ]
          },
          {
            path: '/withdrawalOrder',
            name: 'withdrawalOrder',
            component: withdrawalOrder,
            meta: {
              title: "提现订单查询"
            },
            children: [{
              path: '/TorderDetails',
              name: 'TorderDetails',
              component: orderDetails,
              meta: {
                title: "提现订单详情"
              }
            }, ]
          },
          {
            path: '/withdrawalAudit',
            name: 'withdrawalAudit',
            component: withdrawalAudit,
            meta: {
              title: "提现订单审核"
            },
            children: [{
              path: '/artificialOutMoney',
              name: 'artificialOutMoney',
              component: artificialOutMoney,
              meta: {
                title: "人工出款"
              }
            }, ]
          },
        ]
      },

      /*********************************
       *  
       *            商户管理 
       * 
       ********************************/
      {
        path: '/merchantManage',
        name: 'merchantManage',
        redirect: '/merchantlist',
        component: merchantManage,
        meta: {
          title: "商户管理"
        },
        children: [{
          path: '/merchantlist',
          name: 'merchantlist',
          component: merchantlist,
          meta: {
            title: "商户列表"
          },
          children: [{
              path: '/newMerchant',
              name: 'newMerchant',
              component: newMerchant,
              meta: {
                title: "新增商家"
              }
            },
            {
              path: '/editorMerchant',
              name: 'editorMerchant',
              component: editorMerchant,
              meta: {
                title: "编辑商家"
              }
            },
            {
              path: '/merchantDetails',
              name: 'merchantDetails',
              component: merchantDetails,
              meta: {
                title: "商家详情"
              }
            },
            {
              path: '/balanceEditor',
              name: 'balanceEditor',
              component: balanceEditor,
              meta: {
                title: "余额调整"
              }
            },
          ]
        }]
      },

      /*********************************
       *  
       *            用户管理 
       * 
       ********************************/

      {
        path: '/userManage',
        name: 'userManage',
        redirect: '/userList',
        component: userManage,
        meta: {
          title: "用户管理"
        },
        children: [{
          path: '/userList',
          name: 'userList',
          component: userList,
          meta: {
            title: "用户列表"
          },
          children: [{
              path: '/userBalanceEditor',
              name: 'userBalanceEditor',
              component: userBalanceEditor,
              meta: {
                title: "余额调整"
              },
            },
            {
              path: '/userDetails',
              name: 'userDetails',
              component: userDetails,
              meta: {
                title: "用户详情"
              }
            }
          ]
        }],
      },


      /*********************************
       *  
       *            通道管理 
       * 
       ********************************/
      {
        path: '/channelManage',
        name: 'channelManage',
        redirect: '/rechargeableChannelList',
        component: channelManage,
        meta: {
          title: "通道管理"
        },
        children: [{
            path: '/rechargeableChannelList',
            name: 'rechargeableChannelList',
            component: rechargeableChannelList,
            meta: {
              title: "充值通道列表"
            },
            children: [{
              path: '/newRechargeableChannel',
              name: 'newRechargeableChannel',
              component: newRechargeableChannel,
              meta: {
                title: "新建充值通道"
              }
            }, ]
          },
          {
            path: '/insteadChannelList',
            name: 'insteadChannelList',
            component: insteadChannelList,
            meta: {
              title: "代付通道列表"
            },
            children: [{
              path: '/newInsteadChannel',
              name: 'newInsteadChannel',
              component: newInsteadChannel,
              meta: {
                title: "新建代付通道"
              }
            }, ]
          },
          {
            path: '/guideRuleList',
            name: 'guideRuleList',
            component: guideRuleList,
            meta: {
              title: "引导规则列表"
            },
            children: [{
              path: '/newGuideRule',
              name: 'newGuideRule',
              component: newGuideRule,
              meta: {
                title: "新建引导规则"
              }
            }, ]
          },
        ]
      },




      /*******************************
            系统管理
      *******************************/



      {
        path: '/systemManage',
        name: 'systemManage',
        redirect: '/ChangePassword',
        component: systemManage,
        meta: {
          title: "系统管理"
        },
        children: [{
          path: '/ChangePassword',
          name: 'ChangePassword',
          component: ChangePassword,
          meta: {
            title: "修改密码"
          },
        }],
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