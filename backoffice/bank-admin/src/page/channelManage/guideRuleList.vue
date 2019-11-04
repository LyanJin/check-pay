<template>
  <main>
    <main v-if="this.$route.name == 'guideRuleList'">
      <section class="main">
        <el-button size="medium" type="primary" @click="newChannel"
          >新建+</el-button
        >
      </section>

      <!-- 提现订单展示列表 -->
      <section class="main">
        <el-table :data="dataLidt">
          <el-table-column align="center" prop="router_id" label="引导编号">
          </el-table-column>
          <el-table-column align="center" label="商户">
            <div slot-scope="scope">
              <div v-if="scope.row.merchants.length == 0">
                全部
              </div>
              <div v-for="item in scope.row.merchants" :key="item">
                <p>{{ item }}</p>
              </div>
            </div>
          </el-table-column>

          <el-table-column align="center" label="用户ID">
            <div slot-scope="scope">
              <div v-if="scope.row.uid_list.length == 0">
                全部
              </div>
              <div v-for="item in scope.row.uid_list" :key="item">
                <p>{{ item }}</p>
              </div>
            </div>
          </el-table-column>

          <el-table-column align="center" label="接入类型">
            <div slot-scope="scope">
              <div>
                {{ scope.row.interface.desc }}
              </div>
            </div>
          </el-table-column>

          <el-table-column align="center" label="交易金额">
            <div slot-scope="scope">
              <span>
                {{ scope.row.amount_min }} - {{ scope.row.amount_max }}
              </span>
            </div>
          </el-table-column>

          <el-table-column
            align="center"
            prop="create_time"
            sortable
            label="创建时间"
          ></el-table-column>
          <el-table-column align="center" fixed="right" label="操作">
            <div slot-scope="scope">
              <el-button
                @click="detailClick(scope.row)"
                type="text"
                size="small"
              >
                编辑
              </el-button>
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

import { ruleList } from '@/api/getData'


export default {
  data () {
    return {
      dataLidt: null,
    }
  },

  activated () {
    this.init()
  },
  methods: {
    async init () {
      const res = await ruleList()
      if (res) {
        this.dataLidt = res.data.rules
      }
    },
    // 编辑商家
    detailClick (data) {
      this.$router.push({ path: 'newGuideRule', query: { data: data } })
    },
    // 新建
    newChannel () {
      console.warn(this.dataLidt)
      this.$router.push({ path: 'newGuideRule' })
    },
  },
  watch: {
    "$route" (to) { //监听路由是否变化
      if (to.name == 'guideRuleList') {
        this.init();//重新加载数据
      }
    }
  },
}
</script>

<style lang="less" scoped>
</style>


