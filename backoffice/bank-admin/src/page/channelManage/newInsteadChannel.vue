<template>
  <main id="newInsteadChannel">
    <section class="main">
      <el-form
        :model="channelForm"
        :rules="rules"
        ref="channelForm"
        label-width="140px"
        class="demo-ruleForm"
      >
        <el-form-item label="通道：" prop="channel_id">
          <el-input
            v-if="disabled"
            placeholder="请输入内容"
            v-model="providerInfo.channel_desc"
            maxlength="20"
            readonly
          >
          </el-input>
          <el-select
            v-else
            @change="recharge"
            v-model="channel_id"
            placeholder="请选择"
          >
            <el-option
              v-for="item in config.channel_config"
              :key="item.id"
              :label="item.channel_desc"
              :value="item.channel_id"
            >
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="支付公司：">
          <el-input
            placeholder="请输入内容"
            readonly
            v-model="providerInfo.provider"
            maxlength="20"
          >
          </el-input
        ></el-form-item>

        <el-form-item label="商户号：">
          <el-input
            maxlength="40"
            readonly
            placeholder="请输入内容"
            v-model="providerInfo.id"
            clearable
          >
          </el-input>
        </el-form-item>

        <el-form-item label="成本费率：" prop="fee">
          <el-input
            maxlength="12"
            placeholder="请输入内容"
            v-model="channelForm.fee"
            clearable
          >
            <el-select
              style="width: 90px;"
              v-model="channelForm.fee_type"
              slot="append"
              placeholder="请选择"
            >
              <el-option label="%/笔" value="1"></el-option>
              <el-option label="元/笔" value="2"></el-option>
            </el-select>
          </el-input>
        </el-form-item>

        <el-form-item label="单笔交易限额：" prop="limit_per_min">
          <el-form-item class=" error-left" prop="limit_per_max">
            <el-input
              style="width: 45.5%"
              maxlength="12"
              placeholder="请输入内容"
              v-model="channelForm.limit_per_min"
              clearable
            >
            </el-input>
            ——
            <el-input
              maxlength="12"
              style="width: 45.5%"
              placeholder="请输入内容"
              v-model="channelForm.limit_per_max"
              clearable
            >
            </el-input>
          </el-form-item>
        </el-form-item>

        <el-form-item label="日交易限额：" prop="limit_day_max">
          <el-input
            maxlength="12"
            placeholder="请输入内容"
            v-model="channelForm.limit_day_max"
            clearable
          >
          </el-input>
        </el-form-item>

        <el-form-item label="交易时间：" prop="limit">
          <el-time-picker
            is-range
            v-model="channelForm.limit"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            placeholder="选择时间范围"
          >
          </el-time-picker>
        </el-form-item>

        <!-- <el-form-item label="维护时间：" prop="maintain">
          <div class="block">
            <el-date-picker
              v-model="channelForm.maintain"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
            >
            </el-date-picker>
          </div>
        </el-form-item> -->

        <el-form-item label="状态：" prop="state">
          <el-select v-model="channelForm.state" placeholder="请选择">
            <el-option
              v-for="item in config.channel_state"
              :key="item.value"
              :label="item.desc"
              :value="item.value"
            >
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="健康状态：">
          <el-input
            placeholder="请输入内容"
            readonly
            maxlength="20"
            v-model="channelForm.reason"
          >
          </el-input
        ></el-form-item>

        <el-form-item label="支持银行：" prop="banks">
          <el-select
            v-model="channelForm.banks"
            value-key="value"
            multiple
            placeholder="请选择"
          >
            <el-option
              v-for="item in config.banks"
              :key="item.value"
              :label="item.desc"
              :value="item.value"
            >
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitForm('channelForm')">
            提交
          </el-button>
          <el-button @click="$router.go(-1)">取消</el-button>
        </el-form-item>
      </el-form>
    </section>
  </main>
</template>

<script>
import { mapMutations } from 'vuex'
import { channelConfigGet, withdrawAdd, withdrawEdit } from '@/api/getData'

export default {
  data () {
    return {
      disabled: false,     //true 编辑通道  false 新建通道
      config: {},          //配置信息
      channel_id: null,    //默认支付通道
      providerInfo: {
        provider: ''
      },    //默认支付公司信息
      select: null,
      channelForm: {
        channel_id: null,
        id: null,
        fee: 2,
        fee_type: "1",
        limit_per_min: null,
        limit_per_max: null,
        limit_day_max: null,
        start_time: null,
        end_time: null,
        maintain_begin: null,
        maintain_end: null,
        state: '20',
        limit: [new Date(2016, 9, 10, 0, 0), new Date(2016, 9, 10, 23, 59)],
        maintain: null,
        banks: []
      },
      rules: {
        channel_id: [
          { required: true, message: '请选择通道', trigger: 'blur' }
        ],
        fee: [
          { required: true, message: '请输入成本费率', trigger: 'blur' },
          {            validator (rule, value, callback) {
              var reg = /^-?\d{1,4}(?:\.\d{1,2})?$/
              if (reg.test(value) && value < 100) {
                callback()
              } else {
                callback(new Error('请输入小于100不超过2位小数的数字'))
              }
            },
            trigger: 'blur'
          }
        ],
        limit_per_min: [
          { required: true, message: '请输入单笔最小交易限额', trigger: 'blur' },
          {            validator (rule, value, callback) {
              var reg = /^-?\d{1,9}(?:\.\d{1,2})?$/
              if (reg.test(value)) {
                callback()
              } else {
                callback(new Error('请输入不超过2位小数的数字'))
              }
            },
            trigger: 'blur'
          }
        ],
        limit_per_max: [
          { required: true, message: '请输入单笔最大交易限额', trigger: 'blur' },
          {            validator (rule, value, callback) {
              var reg = /^-?\d{1,9}(?:\.\d{1,2})?$/
              if (reg.test(value)) {
                callback()
              } else {
                callback(new Error('请输入不超过2位小数的数字'))
              }
            },
            trigger: 'blur'
          }
        ],
        limit_day_max: [
          { required: true, message: '请输入日交易限额', trigger: 'blur' },
          {            validator (rule, value, callback) {
              var reg = /^-?\d{1,9}(?:\.\d{1,2})?$/
              if (reg.test(value)) {
                callback()
              } else {
                callback(new Error('请输入不超过2位小数的数字'))
              }
            },
            trigger: 'blur'
          }
        ],
        limit: [
          { required: true, message: '请选择交易时间', trigger: 'blur' }
        ],
        banks: [
          { required: true, message: '请选择支持银行', trigger: 'blur' }
        ],
      },

    }
  },
  async activated () {
    // 初始化获取配置信息
    let res = await channelConfigGet({ pay_type: 2 })
    if (res) {
      this.config = res.data
      if (res.data.channel_config[0]) {
        this.providerInfo = res.data.channel_config[0]
        this.channel_id = this.providerInfo.channel_id
      } else {
        this.providerInfo = {}
      }
    }
    if (this.$route.query.data) {
      this.TITLE('编辑代付通道')
      this.disabled = true
      // 页面数据回显
      this.providerInfo = {
        channel_id: Number(this.$route.query.data.channel_id),
        id: this.$route.query.data.id,
        provider: this.$route.query.data.provider ? this.$route.query.data.provider : '',
        channel_desc: this.$route.query.data.channel_desc,
      }
      // 数据回显
      this.channelForm.fee = this.$route.query.data.fee
      this.channelForm.reason = this.$route.query.data.reason
      this.channelForm.limit_day_max = this.$route.query.data.limit_day_max
      this.channelForm.limit_per_max = this.$route.query.data.limit_per_max
      this.channelForm.limit_per_min = this.$route.query.data.limit_per_min
      this.channelForm.banks = this.$route.query.data.banks
      this.channelForm.state = this.$route.query.data.state.value
      this.channelForm.fee_type = this.$route.query.data.fee_type.value

      // 交易时间
      this.channelForm.limit = ['2018-9-10 ' + this.$route.query.data.trade_start_time, '2018-9-10 ' + this.$route.query.data.trade_end_time]
      // 维护时间
      if (this.$route.query.data.main_time.maintain_begin && this.$route.query.data.main_time.maintain_end) {
        this.channelForm.maintain = [this.$route.query.data.main_time.maintain_begin, this.$route.query.data.main_time.maintain_end]
      }
    } else {
      this.disabled = false
      this.channelForm = {
        fee_type: "1",
        state: '20',
        limit: [new Date(2016, 9, 10, 0, 0), new Date(2016, 9, 10, 23, 59)],
      }
    }


  },

  methods: {
    ...mapMutations([
      'TITLE'
    ]),
    getTime (time, type = true) {
      var date = new Date(time);
      let date_value
      if (type) {
        date_value = date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate() + ' ' + date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds();
      } else {
        date_value = date.getHours() + ':' + date.getMinutes();
      }
      return date_value
    },
    // 更新支付公司
    async recharge (data) {
      let obj = {};
      obj = this.config.channel_config.find((item) => {
        return item.channel_id === data;
      });
      this.providerInfo = obj
    },
    // 提交
    async submitForm (formName) {
      this.channelForm.channel_id = this.providerInfo.channel_id
      this.channelForm.id = this.providerInfo.id
      this.channelForm.priority = String(this.providerInfo.channel_id)
      this.$refs[formName].validate((valid) => {
        if (valid) {
          if (Number(this.channelForm.limit_per_min) >= Number(this.channelForm.limit_per_max)) {
            this.$message.error('单笔交易限额最大值要大于最小值');
            this.channelForm.limit_per_max = null
          } else {
            this.channelForm.start_time = this.getTime(this.channelForm.limit[0], false)
            this.channelForm.end_time = this.getTime(this.channelForm.limit[1], false)
            if (this.channelForm.maintain) {
              this.channelForm.maintain_begin = this.getTime(this.channelForm.maintain[0])
              this.channelForm.maintain_end = this.getTime(this.channelForm.maintain[1])
            }
            this.Add(this.channelForm)
          }
          console.warn(this.channelForm)
        } else {
          return false;
        }
      });
    },
    async Add (data) {
      let res
      if (this.$route.query.data) {
        res = await withdrawEdit(data)
      } else {
        res = await withdrawAdd(data)
      }
      console.warn(res)
      if (res) {
        this.$message({
          message: '提交成功',
          type: 'success'
        });
        setTimeout(() => {
          this.$router.go(-1)
        }, 1000)
      }
    },
  },
  //离开当前页面
  deactivated () {
    this.TITLE(null)
  },
}
</script>

<style lang="less">
@import "../../style/mixin";
#newInsteadChannel {
  .main {
    .demo-ruleForm {
      width: 620px;
      margin: auto;
    }
    .el-select,
    .el-date-editor {
      width: 100%;
    }
    .error-left {
      .el-form-item__error {
        left: 54%;
      }
    }
  }
}
</style>