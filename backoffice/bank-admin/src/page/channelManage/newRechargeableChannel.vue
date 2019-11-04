<template>
  <main id="newRechargeableChannel">
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
            maxlength="20"
            v-model="providerInfo.provider"
          >
          </el-input
        ></el-form-item>

        <el-form-item label="支付类型：">
          <el-input
            placeholder="请输入内容"
            maxlength="20"
            v-model="providerInfo.payment_type"
            readonly
          >
          </el-input>
        </el-form-item>

        <el-form-item label="支付方式：">
          <el-input
            placeholder="请输入内容"
            readonly
            maxlength="20"
            v-model="providerInfo.payment_method"
          >
          </el-input>
        </el-form-item>

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

        <el-form-item label="结算方式：" prop="settlement_type">
          <el-select v-model="channelForm.settlement_type" placeholder="请选择">
            <el-option
              v-for="item in config.settlement_type"
              :key="item.value"
              :label="item.name"
              :value="item.value"
            >
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="交易时间：" prop="start">
          <el-form-item class=" error-left" prop="end">
            <el-time-picker
              style="width: 45.5%"
              v-model="channelForm.start"
              placeholder="开始时间"
            >
            </el-time-picker>
            ——
            <el-time-picker
              style="width: 45.5%"
              v-model="channelForm.end"
              placeholder="结束时间"
            >
            </el-time-picker>
          </el-form-item>
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

        <el-form-item label="适用商户：" prop="merchants">
          <el-select
            v-model="channelForm.merchants"
            value-key="value"
            multiple
            placeholder="默认使用全部"
          >
            <el-option
              v-for="item in merchant_names"
              :key="item.name"
              :label="item.name"
              :value="item.name"
            >
            </el-option>
          </el-select>
        </el-form-item>

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

        <el-form-item label="优先级：" prop="state">
          <el-input
            maxlength="12"
            placeholder="数字越小优先级越高"
            v-model="channelForm.priority"
            clearable
          >
          </el-input>
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
import { channelConfigGet, depositEdit, depositAdd, configGetunt, router2Update } from '@/api/getData'

export default {
  data () {
    return {
      disabled: false,     //true 编辑通道  false 新建通道
      config: {},          //配置信息
      channel_id: null,      //默认支付通道
      providerInfo: {
        provider: ''
      },    //默认支付公司信息
      merchant_names: null,
      channelForm: {
        channel_id: null,
        id: null,
        fee: null,
        fee_type: "1",
        limit_per_min: null,
        limit_per_max: null,
        limit_day_max: null,
        start_time: null,
        start: new Date(2016, 9, 10, 0), //start_time值的容器防止点击后提交失败数据类型改变
        end_time: null,
        end: new Date(2016, 9, 10, 23, 59), //end_time值的容器防止点击后提交失败数据类型改变
        maintain_begin: null,
        maintain_end: null,
        state: '20',
        settlement_type: null,
        maintain: null,
        priority: null
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
          },
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
        settlement_type: [
          { required: true, message: '请选择结算方式', trigger: 'blur' }
        ],
        start: [
          { required: true, message: '请选择开始交易时间', trigger: 'blur' }
        ],
        end: [
          { required: true, message: '请选择结束交易时间', trigger: 'blur' }
        ],
      },
    }
  },
  async activated () {
    // 初始化获取配置信息
    let data = await configGetunt()
    if (data) {
      this.merchant_names = data.data.merchant_names
    }

    // 初始化获取配置信息
    let res = await channelConfigGet({ pay_type: 1 })
    if (res) {
      this.config = res.data
      if (res.data.channel_config[0]) {
        this.providerInfo = res.data.channel_config[0]
        this.channel_id = this.providerInfo.channel_id
      } else {
        this.providerInfo = {}
      }
    }

    console.warn(this.$route.params.data)
    if (this.$route.params.data) {
      this.TITLE('编辑充值通道')
      this.disabled = true
      this.providerInfo = {
        channel_id: Number(this.$route.params.data.channel_id),
        id: this.$route.params.data.id,
        payment_method: this.$route.params.data.payment_method.desc,
        payment_type: this.$route.params.data.payment_type.desc,
        provider: this.$route.params.data.provider ? this.$route.params.data.provider : '',
        channel_desc: this.$route.params.data.channel_desc,
      }
      this.channelForm.fee = this.$route.params.data.fee
      this.channelForm.reason = this.$route.params.data.reason
      this.channelForm.limit_day_max = this.$route.params.data.limit_day_max
      this.channelForm.limit_per_max = this.$route.params.data.limit_per_max
      this.channelForm.limit_per_min = this.$route.params.data.limit_per_min
      this.channelForm.fee_type = this.$route.params.data.fee_type.value
      this.channelForm.merchants = this.$route.params.data.merchants

      this.channelForm.priority = this.$route.params.data.priority
      this.channelForm.settlement_type = this.$route.params.data.settlement_type.key
      this.channelForm.state = this.$route.params.data.state.value
      // 交易时间
      this.channelForm.start = new Date('2018-9-10 ' + this.$route.params.data.trade_start_time)
      this.channelForm.end = new Date('2018-9-10 ' + this.$route.params.data.trade_end_time)

      // 维护时间
      if (this.$route.params.data.main_time.maintain_begin && this.$route.params.data.main_time.maintain_end) {
        this.channelForm.maintain = [this.$route.params.data.main_time.maintain_begin, this.$route.params.data.main_time.maintain_end]
      }
    } else {
      this.disabled = false
      this.channelForm = {
        fee_type: "1",
        state: '20',
        start: new Date(2016, 9, 10, 0),
        end: new Date(2016, 9, 10, 23, 59),
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
      console.warn(data)
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
      if (!this.channelForm.priority) {
        this.channelForm.priority = this.providerInfo.channel_id ? String(this.providerInfo.channel_id) : null
      }
      this.$refs[formName].validate((valid) => {
        if (valid) {
          if (Number(this.channelForm.limit_per_min) >= Number(this.channelForm.limit_per_max)) {
            this.$message.error('单笔交易限额最大值要大于最小值');
            this.channelForm.limit_per_max = null
          } else {
            this.channelForm.start_time = this.getTime(this.channelForm.start, false)
            this.channelForm.end_time = this.getTime(this.channelForm.end, false)
            console.warn(this.channelForm.start_time)
            if (this.channelForm.maintain) {
              this.channelForm.maintain_begin = this.getTime(this.channelForm.maintain[0])
              this.channelForm.maintain_end = this.getTime(this.channelForm.maintain[1])
            }
            this.Add(this.channelForm)
          }
          console.warn(this.channelForm)
        } else {
          console.log('error submit!!');
          return false;
        }
      });
    },
    async Add (data) {
      let res
      let params = {
        channel: data.channel_id,
        merchants: data.merchants
      }
      let routerRes = await router2Update(params)
      console.warn(routerRes)
      if (this.$route.params.data) {
        res = await depositEdit(data)
      } else {
        res = await depositAdd(data)
      }

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
#newRechargeableChannel {
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