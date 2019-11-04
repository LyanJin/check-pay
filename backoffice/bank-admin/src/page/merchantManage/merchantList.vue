<template>
  <main>
    <main class="fillcontain clear" v-if="this.$route.name == 'merchantlist'">
      <section class="main">
        <el-button size="medium" type="primary" @click="newmerchant"
          >新建+</el-button
        >
      </section>

      <!-- 提现订单展示列表 -->
      <section class="main" id="building-top">
        <el-table :data="dataLidt" :cell-class-name="cellStyle">
          <el-table-column align="center" prop="id" label="商户编号">
          </el-table-column>
          <el-table-column align="center" prop="name" label="商户名称">
          </el-table-column>
          <el-table-column align="center" label="总余额">
            <div slot-scope="scope">
              {{ scope.row.balance_total | NumFormat }}
            </div>
          </el-table-column>
          <el-table-column align="center" label="可用余额">
            <div slot-scope="scope">
              {{ scope.row.balance_available | NumFormat }}
            </div>
          </el-table-column>
          <el-table-column align="center" label="在途余额">
            <div slot-scope="scope">
              {{ scope.row.balance_income | NumFormat }}
            </div>
          </el-table-column>
          <el-table-column align="center" label="冻结余额">
            <div slot-scope="scope">
              {{ scope.row.balance_frozen | NumFormat }}
            </div>
          </el-table-column>
          <el-table-column align="center" label="商户类型">
            <div slot-scope="scope">
              <span>{{ scope.row.type | merchantType }}</span>
            </div>
          </el-table-column>
          <el-table-column align="center" prop="domains" label="域名">
          </el-table-column>
          <el-table-column align="center" fixed="right" label="操作">
            <div slot-scope="scope">
              <el-button @click="detailClick(scope.row)" type="text"
                >编辑</el-button
              >
              <el-dropdown style="margin-left:10px;" @command="handleCommand">
                <el-button type="text"
                  >更多
                  <i class="el-icon-arrow-down el-icon--right"></i>
                </el-button>
                <el-dropdown-menu slot="dropdown">
                  <el-dropdown-item
                    :command="{ id: scope.row, type: 'Details' }"
                    >详情</el-dropdown-item
                  >
                  <el-dropdown-item :command="{ id: scope.row, type: 'Editor' }"
                    >余额调整</el-dropdown-item
                  >
                </el-dropdown-menu>
              </el-dropdown>
            </div>
          </el-table-column>
        </el-table>
      </section>
    </main>

    <keep-alive v-else>
      <router-view></router-view>
    </keep-alive>
  </main>
</template>

<script>

import { merchantList } from '@/api/getData'
import { setSessStore } from '@/config/mUtils'


export default {
  data () {
    return {
      dataLidt: null,
    }
  },

  activated () {
    this.init();
  },
  methods: {
    async init () {
      const res = await merchantList()
      if (res) {
        this.dataLidt = res.data.merchants
      }
    },
    // 编辑商家
    detailClick (data) {
      this.$router.push({ name: 'editorMerchant', params: { data: data } })
    },
    // 新建
    newmerchant () {
      console.warn(this.dataLidt)
      this.$router.push({ path: 'newMerchant' })
    },

    handleCommand (command) {
      if (command.type == 'Details') {
        //详情
        this.$router.push({ name: 'merchantDetails', params: { data: command.id } })
      } else {
        //余额调整
        // 更新商户余额调整
        command.id.amount = null
        command.id.adjustment_type = null
        command.id.reason = null
        setSessStore('BALANCE_EDIT', command.id)
        this.$router.push({ path: "balanceEditor" })

      }
    },

    cellStyle ({ columnIndex }) {
      if (columnIndex === 7) {//指定列号  
        return 'column'
      } else {
        return ''
      }
    }
  },
  watch: {
    "$route" (to) { //监听路由是否变化
      if (to.name == 'merchantlist') {
        this.init();//重新加载数据
      }
    }
  },
}
</script>

<style lang="less">
@import "../../style/mixin";
.fillcontain {
  #building-top {
    .el-form-item {
      display: inline-block;
      margin-bottom: 12px;
    }
    .el-input {
      width: 40%;
    }
    .column {
      .cell {
        white-space: pre-line;
      }
    }
  }
}
</style>


