<template>
  <div class="manage_page fillcontain">
    <el-row>
      <el-col
        :span="4"
        style="min-height: 100vh;border-right: solid 1px #e6e6e6;background:#f9f9f9"
      >
        <el-menu
          :default-active="defaultActive"
          background-color="#f9f9f9"
          style="min-height: 100%;"
          router
        >
          <router-link to="/home">
            <el-menu-item index="home">
              <i class="el-icon-house"></i>
              首页
            </el-menu-item>
          </router-link>

          <router-link to="/payOrder">
            <el-menu-item index="payOrder">
              <i class="el-icon-notebook-1"></i>
              充值订单查询
            </el-menu-item>
          </router-link>

          <router-link to="/withdrawalOrder">
            <el-menu-item index="withdrawalOrder">
              <i class="el-icon-notebook-2"></i>
              提现订单查询
            </el-menu-item>
          </router-link>
          
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
import { mapState } from 'vuex'


export default {
  data () {
    return {
      // 不缓存的组件
      cashViews: ['balanceEditor', 'fillOrder']
    }
  },

  computed: {
    ...mapState([
      'title'
    ]),
    defaultActive: function () {
      return this.$route.path.replace('/', '');
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
  .el-menu-item {
    height: 70px;
    line-height: 70px;
    font-size: 16px;
  }
}
</style>
