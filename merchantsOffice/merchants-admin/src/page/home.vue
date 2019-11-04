<template>
  <div>
    <section class="data_section">
      <header class="section_title">数据统计</header>
      <el-row :gutter="20" class="main">
        <el-col :span="6">
          <div class="data_list today_head">
            <h4 class="data_title">总余额<i class="blue">总</i></h4>
            <div class="admin">
              <span> {{ allAdminCount.balance_total | NumFormat }}</span>
              <p>元 <i class="el-icon-s-finance"></i></p>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="data_list today_head">
            <h4 class="data_title">可用余额<i class="orange">总</i></h4>
            <div class="admin">
              <span> {{ allAdminCount.available_balance | NumFormat }}</span>
              <p>元 <i class="el-icon-s-finance"></i></p>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="data_list today_head">
            <h4 class="data_title">在途余额<i class="green">总</i></h4>
            <div class="admin">
              <span> {{ allAdminCount.incoming_balance | NumFormat }}</span>
              <p>元 <i class="el-icon-s-finance"></i></p>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="data_list today_head">
            <h4 class="data_title">冻结余额<i class="gray">总</i></h4>
            <div class="admin">
              <span> {{ allAdminCount.frozen_balance | NumFormat }}</span>
              <p>元 <i class="el-icon-s-finance"></i></p>
            </div>
          </div>
        </el-col>
      </el-row>
    </section>
  </div>
</template>

<script>
import { merchantIndex } from '@/api/getData'

export default {
  data () {
    return {
      allAdminCount: {},
    }
  },
  async activated () {
    const data = await merchantIndex()
    if (data) {
      this.allAdminCount = data.data

    }

    console.warn(this.allAdminCount)
  },
  mounted () {

  },
  computed: {

  },
  methods: {
    //   async initData () {
    //     const today = dtime().format('YYYY-MM-DD')
    //     Promise.all([userCount(today), orderCount(today), adminDayCount(today), getUserCount(), getOrderCount(), adminCount()])
    //       .then(res => {
    //         this.userCount = res[0].count;
    //         this.orderCount = res[1].count;
    //         this.adminCount = res[2].count;
    //         this.allUserCount = res[3].count;
    //         this.allOrderCount = res[4].count;
    //         this.allAdminCount = res[5].count;
    //       }).catch(err => {
    //         console.log(err)
    //       })
    //   },
    //   async getSevenData () {
    //     const apiArr = [[], [], []];
    //     this.sevenDay.forEach(item => {
    //       apiArr[0].push(userCount(item))
    //       apiArr[1].push(orderCount(item))
    //       apiArr[2].push(adminDayCount(item))
    //     })
    //     const promiseArr = [...apiArr[0], ...apiArr[1], ...apiArr[2]]
    //     Promise.all(promiseArr).then(res => {
    //       const resArr = [[], [], []];
    //       res.forEach((item, index) => {
    //         if (item.status == 1) {
    //           resArr[Math.floor(index / 7)].push(item.count)
    //         }
    //       })
    //       this.sevenDate = resArr;
    //     }).catch(err => {
    //       console.log(err)
    //     })
    //   }
  }
}
</script>

<style lang="less">
@import "../style/mixin";
.data_section {
  padding: 20px;
  margin-bottom: 40px;
  .main {
    padding: 15px 5px;
    background: #f4f4f4;
    .el-col {
      padding-right: 0 !important;
    }
  }
  .section_title {
    text-align: center;
    font-size: 30px;
    margin-bottom: 10px;
  }
  .data_list {
    font-size: 14px;
    color: #666;
    background: #e5e9f2;
    border: 1px solid #eee;
    .data_title {
      padding: 10px 16px;
      color: #333;
      font-size: 16px;
      border-bottom: 1px solid #eee;
      i {
        font-size: 12px;
        color: #fff;
        border-radius: 3px;
        padding: 0 6px;
        float: right;
        margin-top: 3px;
      }
    }
    .admin {
      padding: 5px 16px;
      font-size: 30px;
      font-weight: 700;
      text-align: right;
      color: #666;
      p {
        font-size: 14px;
        padding: 10px 0;
      }
    }
  }
  .today_head {
    background: #fff;
  }
  .blue {
    background: #20a0ff;
  }
  .gray {
    background: #606266;
  }
  .orange {
    background: #ff9800;
  }
  .green {
    background: #67c23a;
  }
}
.wan {
  .sc(16px, #333);
}
</style>
