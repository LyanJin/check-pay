<template>
  <main class="fillcontain clear">
    <section class="main">
      <el-form ref="form" :model="form" label-width="80px" size="mini">
        <!-- 筛选条件 -->
        <el-form-item label="用户ID">
          <el-input
            v-model="input"
            maxlength="30"
            placeholder="请输入内容"
            clearable
          ></el-input>
        </el-form-item>

        <el-form-item label="订单时间">
          <el-date-picker
            v-model="optionTime"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            :picker-options="pickerOptions"
          >
          </el-date-picker>
        </el-form-item>

        <el-form-item label="账变类型">
          <el-select v-model="form.value" placeholder="请选择" clearable>
            <el-option
              v-for="item in options"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            >
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="onSubmit">查询</el-button>
          <el-button>重置</el-button>
        </el-form-item>
      </el-form>
    </section>

    <!-- 提现订单展示列表 -->

    <section class="main">
      <el-table
        :data="tableData"
        :header-row-style="{
          color: '#333'
        }"
      >
        <el-table-column align="center" prop="date" label="用户ID"> </el-table-column>
        <el-table-column align="center" prop="name" label="系统订单号"> </el-table-column>
        <el-table-column align="center" prop="address" label="变动前余额"> </el-table-column>
        <el-table-column align="center" prop="address" label="交易金额"> </el-table-column>
        <el-table-column align="center" prop="address" label="变动后余额"> </el-table-column>
        <el-table-column align="center" prop="address" label="通道"> </el-table-column>
        <el-table-column align="center" prop="address" label="账变类型"> </el-table-column>
        <el-table-column align="center"
          prop="address"
          sortable
          label="创建时间"
        ></el-table-column>
      </el-table>
      <!-- 分页 -->
      <el-pagination
        @current-change="handleCurrentChange"
        :current-page="currentPage4"
        :page-size="10"
        layout="total, prev, pager, next, jumper"
        :total="400"
        style="margin-top: 20px;text-align: center;"
      >
      </el-pagination>
    </section>
  </main>
</template>

<script>

export default {
  data () {
    return {
      activeName: '全部', //默认显示全部
      optionTime: [],//选择后时间
      pickerOptions: { //设置只能查看前三个月
        disabledDate (time) {
          let curDate = (new Date()).getTime();
          let three = 90 * 24 * 3600 * 1000;
          let threeMonths = curDate - three;
          return time.getTime() > Date.now() || time.getTime() < threeMonths
        }
      },
      input: '',
      options: [{
        value: '选项1',
        label: '黄金糕'
      }, {
        value: '选项2',
        label: '双皮奶'
      }, {
        value: '选项3',
        label: '蚵仔煎'
      }, {
        value: '选项4',
        label: '龙须面'
      }, {
        value: '选项5',
        label: '北京烤鸭'
      }],
      form: {
        orderTime: '',
        value: ''
      },
      tableData: [{
        date: '2016-05-02',
        name: '王小虎',
        address: '上海市普陀区金沙江路 1518 弄'
      }, {
        date: '2016-05-04',
        name: '王小虎',
        address: '上海市普陀区金沙江路 1517 弄'
      },
      {
        date: '2016-05-01',
        name: '王小虎',
        address: '上海市普陀区金沙江路 1519 弄'
      },
      {
        date: '2016-05-01',
        name: '王小虎',
        address: '上海市普陀区金沙江路 1519 弄'
      },
      {
        date: '2016-05-01',
        name: '王小虎',
        address: '上海市普陀区金沙江路 1519 弄'
      },
      {
        date: '2016-05-03',
        name: '王小虎',
        address: '上海市普陀区金沙江路 1516 弄'
      }],
      currentPage4: 1 //页数
    }
  },

  created () {
    //订单时间默认当天
    let Time = new Date() //当前时间
    this.optionTime = [new Date(Time.getFullYear(), Time.getMonth(), Time.getDate()), Time]

  },
  methods: {
    //筛选
    onSubmit () {
      console.log('submit!');
    },
    // 查看订单详情
    detailClick (data) {
      console.log(data)
      this.$router.push({ path: 'orderDetails', query: { restaurant_id: data } })
    },
    // 分页
    handleCurrentChange (val) {
      console.log(`当前页: ${val}`);
    },
    // 人工补单
    fillOrder () {
      this.$router.push({ path: 'fillOrder' })
    }
  },
  watch: {
    activeName: function () {
      console.log(this.activeName)
    }
  }
}
</script>

<style lang="less" scoped>
@import "../../style/mixin";
.fillcontain {
  .main {
    .el-form-item {
      display: inline-block;
      margin-bottom: 12px;
    }
    .money {
      .el-input {
        width: 40%;
      }
    }
  }
  .el-form-item {
    display: inline-block;
  }
}
</style>


