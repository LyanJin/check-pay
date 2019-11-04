<template>
  <div class="manage_page fillcontain">
    <el-row>
      <el-col
        :span="4"
        style="min-height: 100vh;border-right: solid 1px #e6e6e6;background:#f9f9f9 "
      >
        <el-menu
          :default-active="defaultActive"
          style="min-height: 100%;"
          background-color="#f9f9f9"
          router
        >
          <router-link to="/home">
            <el-menu-item index="home">
              <i class="el-icon-house"></i>
              首页
            </el-menu-item>
          </router-link>

          <!-- <el-submenu index="2">
            <template slot="title">
              权限管理
            </template>
            <el-menu-item index="accountManage">账号管理</el-menu-item>
            <el-menu-item index="withdrawalOrder">角色管理</el-menu-item>
            <el-menu-item index="register">添加账户</el-menu-item>
          </el-submenu> -->

          <el-submenu index="tradeManage">
            <template slot="title">
              <i class="el-icon-notebook-1"></i>
              交易管理
            </template>
            <router-link to="/payOrder">
              <el-menu-item index="payOrder">充值订单查询 </el-menu-item>
            </router-link>
            <router-link to="/withdrawalOrder">
              <el-menu-item index="withdrawalOrder">提现订单查询</el-menu-item>
            </router-link>
            <router-link to="/withdrawalAudit">
              <el-menu-item index="withdrawalAudit">提现订单审核</el-menu-item>
            </router-link>
          </el-submenu>

          <el-submenu index="4">
            <template slot="title">
              <i class="el-icon-coin"></i>
              资金管理
            </template>
            <el-menu-item index="userFundsDetail">用户资金明细</el-menu-item>
            <el-menu-item index="merchantFundsDetail">
              商家资金明细
            </el-menu-item>
          </el-submenu>

          <el-submenu index="merchantManage">
            <template slot="title">
              <i class="el-icon-office-building"></i>
              商户管理
            </template>
            <router-link to="/merchantlist">
              <el-menu-item index="merchantlist">商户列表</el-menu-item>
            </router-link>
          </el-submenu>

          <el-submenu index="userManage">
            <template slot="title">
              <i class="el-icon-user"></i>
              用户管理
            </template>

            <router-link to="/userList">
              <el-menu-item index="userList">用户列表</el-menu-item>
            </router-link>
          </el-submenu>

          <el-submenu index="channelManage">
            <template slot="title">
              <i class="el-icon-s-operation"></i>
              通道管理
            </template>
            <router-link to="/rechargeableChannelList">
              <el-menu-item index="rechargeableChannelList">
                充值通道列表
              </el-menu-item>
            </router-link>
            <router-link to="/insteadChannelList">
              <el-menu-item index="insteadChannelList">
                代付通道列表
              </el-menu-item>
            </router-link>
            <router-link to="/guideRuleList">
              <el-menu-item index="guideRuleList">引导规则列表</el-menu-item>
            </router-link>
          </el-submenu>

          <!-- <el-submenu index="8">
            <template slot="title">
              日志管理
            </template>
            <el-menu-item index="">操作日志</el-menu-item>
          </el-submenu> -->

          <el-submenu index="systemManage">
            <template slot="title">
              <i class="el-icon-setting"></i>
              系统管理
            </template>

            <router-link to="/ChangePassword">
              <el-menu-item index="ChangePassword">修改密码</el-menu-item>
            </router-link>
          </el-submenu>
        </el-menu>
      </el-col>
      <el-col :span="20">
        <headTop :title="title"></headTop>
        <keep-alive :exclude="cashViews">
          <router-view></router-view>
        </keep-alive>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import headTop from '../components/headTop'
import { mapMutations, mapState } from 'vuex'
import { noTradeWithdrawListload } from '@/api/getData'
import { getLocalStore, getTimeForm } from '@/config/mUtils'

export default {
  data () {
    return {
      // 不缓存的组件
      cashViews: ['balanceEditor', 'fillOrder', 'userBalanceEditor'],
      time: 10, //定时间隔（秒）
      audio: new Audio("https://" + window.location.host + "/new_order.mp3"),
      withdrawList: {
        page_size: 10,
        page_index: 1,
        begin_time: getTimeForm(new Date(new Date().getFullYear(), new Date().getMonth(), new Date().getDate())),
        end_time: getTimeForm(new Date()),
        state: '10'
      }
    }
  },
  async mounted () {
    if (getLocalStore('token')) {
      const data = await noTradeWithdrawListload(this.withdrawList)
      if (data) {
        // 首次进入直接保存订单数
        this.NEW_ORDER(data.data.total)
        if (data.data.total > 0) {
          this.play()
        }
      }
    }

    /**
     * 
     * 设置定时器实时获取订单
     * 
     */
    clearTimeout(int)
    let int = setInterval(() => {
      this.Order()
    }, this.time * 1000);
  },
  computed: {
    ...mapState([
      'title', 'newOrder'
    ]),
    defaultActive: function () {
      return this.$route.path.replace('/', '');
    }
  },
  methods: {
    ...mapMutations([
      'NEW_ORDER'
    ]),
    // 更新提现新订单
    async Order () {
      if (getLocalStore('token')) {
        this.withdrawList.end_time = getTimeForm(new Date())
        const data = await noTradeWithdrawListload(this.withdrawList)
        if (data) {
          console.warn(data.data.total)
          if (data.data.total && data.data.total > this.newOrder) {
            // 更新提现订单数
            this.NEW_ORDER(data.data.total)
            this.play()
          }
        }
      }
    },

    // 播放音频提示
    play () {
      this.audio.play()
      this.$notify({
        title: '有新的提现订单',
        message: '有新的提现订单，请查看 ',
        type: 'warning',
        onClick: () => {
          this.$router.push('/withdrawalOrder');
        }
      });
    }
  },
  components: {
    headTop,
  },
}
</script>


<style lang="less" scoped>
@import "../style/mixin";

.el-menu {
  border-right: none;
}
</style>
