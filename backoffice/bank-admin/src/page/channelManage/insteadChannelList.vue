<template>
  <main>
    <main v-if="this.$route.name == 'insteadChannelList'">
      <section class="main">
        <el-button size="medium" type="primary" @click="newChannel"
          >新建+</el-button
        >
      </section>

      <!-- 代付通道列表 -->
      <section class="main">
        <el-table :data="dataLidt" :row-class-name="tableRowClassName">
          <el-table-column align="center" prop="provider" label="支付公司">
          </el-table-column>

          <el-table-column align="center" prop="channel_id" label="通道">
          </el-table-column>

          <el-table-column align="center" prop="id" label="通道商户号">
          </el-table-column>

          <el-table-column align="center" label="成本费率">
            <div slot-scope="scope">
              <span> {{ scope.row.fee }}{{ scope.row.fee_type.desc }} </span>
            </div>
          </el-table-column>

          <el-table-column align="center" label="单笔交易限额" width="140">
            <div slot-scope="scope">
              <span>
                {{ scope.row.limit_per_min }} - {{ scope.row.limit_per_max }}
              </span>
            </div>
          </el-table-column>
          <el-table-column
            align="center"
            prop="limit_day_max"
            label="日交易限额"
          >
          </el-table-column>

          <el-table-column
            align="center"
            prop="domains"
            label="交易时间"
            width="110"
          >
            <div slot-scope="scope">
              <span>
                {{ scope.row.trade_start_time }} ~
                {{ scope.row.trade_end_time }}
              </span>
            </div>
          </el-table-column>

          <el-table-column align="center" prop="state.desc" label="状态">
          </el-table-column>

          <el-table-column align="center" prop="reason" label="健康状态">
          </el-table-column>

          <el-table-column align="center" prop="banks.length" label="支持银行">
          </el-table-column>

          <!-- <el-table-column align="center" label="维护时间" width="180">
            <div slot-scope="scope">
              <span v-if="scope.row.main_time.maintain_begin">
                {{ scope.row.main_time.maintain_begin }} ~
                {{ scope.row.main_time.maintain_end }}
              </span>
            </div>
          </el-table-column> -->

          <el-table-column align="center" fixed="right" label="操作">
            <div slot-scope="scope">
              <el-button
                @click="detailClick(scope.row)"
                type="text"
                size="small"
                >编辑</el-button
              >
              <el-popover
                placement="left"
                trigger="click"
                v-if="scope.row.state.desc == '已下架'"
              >
                <p>确定删除这条通道吗？</p>
                <div style="text-align: right; margin: 0">
                  <el-button
                    size="mini"
                    type="primary"
                    @click="Delete(scope.row, scope.$index)"
                  >
                    确定
                  </el-button>
                </div>
                <el-button type="text" size="small" slot="reference"
                  >删除</el-button
                >
              </el-popover>
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
import { withdrawList, withdrawDel } from '@/api/getData'


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
    // 列表根据是否上架改变样式
    tableRowClassName ({ row }) {
      if (row.state.value == 40) {
        return 'warning-row';
      } else if (row.state.value == 10) {
        return 'success-row';
      }
      return '';
    },
    async init () {
      const res = await withdrawList()
      if (res) {
        this.dataLidt = res.data.withdraws
      }
    },
    // 编辑商家
    detailClick (data) {
      this.$router.push({ path: 'newInsteadChannel', query: { data: data } })
    },
    // 新建
    newChannel () {
      this.$router.push({ path: 'newInsteadChannel' })
    },
    // 删除代付通道
    async Delete (item, index) {
      console.warn('Delete', item)
      item.fee_type = item.fee_type.value
      item.state = item.state.value
      item.start_time = item.trade_start_time
      item.end_time = item.trade_end_time
      const res = await withdrawDel(item)
      if (res) {
        this.dataLidt.splice(index, 1)
      } else {
        item.state = { desc: "已下架", value: "40" }
      }
    },
  },
  watch: {
    "$route" (to) { //监听路由是否变化
      if (to.name == 'insteadChannelList') {
        this.init();//重新加载数据
      }
    }
  },
}
</script>

<style lang="less" scoped>
</style>


