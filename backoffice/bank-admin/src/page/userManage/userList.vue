<template>
  <main>
    <main class="clear" v-if="this.$route.name == 'userList'">
      <section class="main">
        <el-form
          ref="userSearchForm"
          :model="userSearchForm"
          label-width="80px"
        >
          <!-- 筛选条件 -->
          <el-form-item label="手机号" label-width="90px">
            <el-input
              v-model="userSearchForm.phone_number"
              placeholder="请输入内容"
              maxlength="20"
              clearable
            ></el-input>
          </el-form-item>

          <el-form-item label="注册时间">
            <el-date-picker
              v-model="optionTime"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              :default-time="defaultTime"
              :picker-options="pickerOptions"
            >
            </el-date-picker>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="onSubmit">查询</el-button>
          </el-form-item>
        </el-form>
      </section>

      <!-- 提现订单展示列表 -->
      <section class="main" v-if="dataLidt">
        <el-table :data="dataLidt">
          <el-table-column align="center" prop="user_id" label="用户ID">
          </el-table-column>

          <el-table-column align="center" prop="phone_number" label="手机号">
          </el-table-column>

          <el-table-column align="center" prop="type" label="用户类型">
          </el-table-column>

          <el-table-column align="center" prop="source" label="用户来源">
          </el-table-column>

          <el-table-column align="center" prop="available_bl" label="可用金币">
          </el-table-column>

          <el-table-column
            align="center"
            prop="register_datetime"
            sortable
            label="注册时间"
            width="165"
          >
          </el-table-column>

          <el-table-column align="center" label="状态">
            <div slot-scope="scope">
              <span>
                {{ scope.row.state == "ACTIVE" ? "正常" : "禁止提现" }}
              </span>
            </div>
          </el-table-column>

          <el-table-column align="center" fixed="right" label="操作">
            <div slot-scope="scope">
              <el-button @click="balance(scope.row)" type="text"
                >余额调整</el-button
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
                </el-dropdown-menu>
              </el-dropdown>
            </div>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <el-pagination
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-size="10"
          layout="total, prev, pager, next, jumper"
          :total="total"
          style="margin-top: 20px;text-align: center;"
        >
        </el-pagination>
      </section>
    </main>

    <keep-alive v-else>
      <router-view></router-view>
    </keep-alive>
  </main>
</template>

<script>

import { userManageuserList } from '@/api/getData'
import { setSessStore, getTimeForm } from '@/config/mUtils'

export default {
  data () {
    return {
      pickerOptions: { //设置只能选择过去时间
        disabledDate (time) {
          let curDate = (new Date()).getTime();
          let three = 7 * 24 * 3600 * 1000;
          let threeMonths = curDate - three;
          return time.getTime() > (Date.now() + 24 * 3600 * 1000) || time.getTime() < threeMonths
        },
      },
      dataLidt: null,
      currentPage: 1,        //页数
      // 筛选条件列表
      userSearchForm: {
        phone_number: null,
        start_datetime: null,
        end_datetime: null,
        page_size: 10,
        page_index: 1
      },
      optionTime: [],// 注册时间
      defaultTime: ['00:00:00', '23:59:59'],
    }
  },

  activated () {
    console.warn(1)
    this.init()
  },
  methods: {
    async init () {
      this.userSearchForm.page_index = this.currentPage
      const res = await userManageuserList(this.userSearchForm)
      if (res) {
        this.dataLidt = res.data.entries
        this.total = Number(res.data.total)
        console.warn(res.data)
      }
    },
    //筛选
    onSubmit () {
      this.currentPage = 1
      this.init()
    },

    // 分页
    handleCurrentChange (val) {
      this.currentPage = val
      this.init()
    },

    // 新建
    newmerchant () {
      console.warn(this.dataLidt)
      this.$router.push({ path: 'newMerchant' })
    },
    //余额调整
    balance (data) {
      // 更新商户余额调整
      console.warn(data)
      data.amount = ''
      data.adjust_type = ''
      setSessStore('USER_BALANCE_EDIT', data)
      this.$router.push({ name: "userBalanceEditor" })

    },
    handleCommand (command) {
      if (command.type == 'Details') {
        //详情
        console.warn(command.id)
        this.$router.push({ name: 'userDetails', params: { userInfo: command.id } })
      }
    },
  },
  watch: {
    "$route" (to) { //监听路由是否变化
      if (to.name == 'userList') {
        this.init();//重新加载数据
      }
    },
    optionTime: function () {
      if (this.optionTime && this.optionTime.length > 0) {
        this.userSearchForm.start_datetime = getTimeForm(this.optionTime[0])
        this.userSearchForm.end_datetime = getTimeForm(this.optionTime[1])
      } else {
        this.userSearchForm.start_datetime = null
        this.userSearchForm.end_datetime = null
      }
    }
  }
}
</script>

<style lang="less" scoped>
@import "../../style/mixin";
.fillcontain {
  .el-form-item {
    display: inline-block;
    margin-bottom: 12px;
  }
  .el-table {
    .cell {
      white-space: pre-line;
    }
  }
}
</style>


