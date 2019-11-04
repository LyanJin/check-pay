<template>
  <main class="fillcontain clear">
    <section class="main">
      <el-form ref="form" :model="form" label-width="80px" size="mini">
        <!-- 筛选条件 -->
        <el-form-item label="账户">
          <el-input
            v-model="input"
            placeholder="请输入内容"
            maxlength="30"
            clearable
          ></el-input>
        </el-form-item>

        <el-form-item label="状态">
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
        <el-table-column align="center" prop="date" label="账户"> </el-table-column>
        <el-table-column align="center" prop="name" label="角色"> </el-table-column>
        <el-table-column align="center"
          prop="address"
          sortable
          label="创建时间"
        ></el-table-column>
        <el-table-column align="center" prop="address" label="创建人"> </el-table-column>
        <el-table-column align="center" label="状态">
          <div slot-scope="scope">
            <el-switch
              v-model="scope.row.switch"
              active-color="#13ce66"
              active-text="启用"
              inactive-text="停用"
            >
            </el-switch>
          </div>
        </el-table-column>
        <el-table-column align="center" fixed="right" label="操作">
          <div slot-scope="scope">
            <el-button @click="detailClick(scope.row)" type="text" size="small"
              >编辑</el-button
            >
            <el-button type="text" size="small">更多</el-button>
          </div>
        </el-table-column>
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
        switch: true,
        address: '上海市普陀区金沙江路 1518 弄'
      }, {
        date: '2016-05-04',
        name: '王小虎',
        switch: false,
        address: '上海市普陀区金沙江路 1517 弄'
      },
      {
        date: '2016-05-01',
        name: '王小虎',
        switch: false,
        address: '上海市普陀区金沙江路 1519 弄'
      },
      {
        date: '2016-05-01',
        name: '王小虎',
        switch: false,
        address: '上海市普陀区金沙江路 1519 弄'
      },
      {
        date: '2016-05-01',
        name: '王小虎',
        switch: false,
        address: '上海市普陀区金沙江路 1519 弄'
      },
      {
        date: '2016-05-03',
        name: '王小虎',
        switch: false,
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


