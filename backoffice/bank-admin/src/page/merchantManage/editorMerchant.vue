<template>
  <main id="editormerchant" v-if="data">
    <section class="merchantInfo">
      <h4>基本信息</h4>
      <ul>
        <li>
          商户名称：<span> {{ data.name }}</span>
        </li>
        <li>
          商户类型：<span> {{ data.type | merchantType }}</span>
        </li>
      </ul>
    </section>

    <section class="main">
      <h4>费率管理</h4>
      <el-form
        :model="ruleForm"
        ref="ruleForm"
        label-width="120px"
        class="demo-ruleForm"
      >
        <el-form-item
          v-for="(domain, index) in ruleForm.deposit_info"
          :label="'充值费率' + (index + 1)"
          :key="domain.key"
          :prop="'deposit_info.' + index + '.name'"
          :rules="{
            required: true,
            message: '请选择支付方式',
            trigger: 'blur'
          }"
        >
          <el-form-item
            :key="domain.key"
            class="error-left"
            :prop="'deposit_info.' + index + '.value'"
            :rules="{
              required: true,
              message: '请输入充值费率',
              trigger: 'blur'
            }"
          >
            <el-select
              style="width:50%"
              v-model="domain.name"
              placeholder="请选择支付方式"
              @change="upinfo"
            >
              <el-option
                v-for="item in payment_methods"
                :key="item.value"
                :label="item.desc"
                :value="item.value"
                :disabled="item.disabled"
              >
              </el-option>
            </el-select>
            -
            <el-input
              style="width:25%"
              maxlength="10"
              v-model="domain.value"
            ></el-input>
            %
            <el-button
              v-if="index > 0"
              style="margin-left:6px"
              @click.prevent="removeDomain(domain)"
              >删除</el-button
            >
          </el-form-item>
        </el-form-item>

        <el-form-item style="text-align: center;">
          <el-button @click="addDomain">添加费率</el-button>
        </el-form-item>

        <el-form-item
          label="提现费率"
          prop="withdraw_info.value"
          :rules="{
            required: true,
            message: '费率不能为空',
            trigger: 'blur'
          }"
        >
          <el-input
            style="width:70%"
            placeholder="请输入费率"
            v-model="ruleForm.withdraw_info.value"
            maxlength="12"
          ></el-input>
          -
          <el-select
            style="width:20%"
            v-model="ruleForm.withdraw_info.fee_type"
            placeholder="请选择支付方式"
          >
            <el-option
              v-for="item in options"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            >
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item
          label="提现扣费类型"
          prop="withdraw_info.cost_type"
          :rules="{
            required: true,
            message: '类型不能为空',
            trigger: 'blur'
          }"
        >
          <el-select
            style="width:94%"
            v-model="ruleForm.withdraw_info.cost_type"
            placeholder="请选择支付方式"
          >
            <el-option
              v-for="item in costType"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            >
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitForm('ruleForm')"
            >提交</el-button
          >
        </el-form-item>
      </el-form>
    </section>
  </main>
</template>

<script>
import { configGetunt, feeEdit } from '@/api/getData'

export default {
  data () {
    return {
      data: null,
      ruleForm: {
        name: null,
        deposit_info: [{
          name: null,
          value: '',
          fee_type: '1'
        }],
        withdraw_info: {
          value: '',
          fee_type: '1',
          cost_type: ''
        }
      },
      merchant_names: null,  //商户名称
      payment_methods: null, //充值方式
      // 提款费率类型
      options: [{
        value: '2',
        label: '元/笔'
      }, {
        value: '1',
        label: '%/笔'
      }],
      costType: [{
        value: 'MERCHANT',
        label: '扣商户'
      }, {
        value: 'USER',
        label: '扣用户'
      }],
    }
  },
  async activated () {
    if (this.$route.params.data) {
      this.data = this.$route.params.data
      console.warn(this.data)
    } else {
      this.$router.go(-1)
      return
    }
    // 初始化获取配置信息
    let res = await configGetunt()
    this.merchant_names = res.data.merchant_names
    this.payment_methods = res.data.payment_methods
    // 获取商户名称
    this.ruleForm.name = this.data.name
    // 获取商户充值费率
    let deposit = []
    for (let i = 0; i < this.data.channel_fees.deposit.length; i++) {
      this.data.channel_fees.deposit[i].rate = this.data.channel_fees.deposit[i].rate.replace(/\s+|%\/笔|元\/笔/g, "")
      let data = {}
      data.name = this.data.channel_fees.deposit[i].value
      data.value = this.data.channel_fees.deposit[i].rate
      data.fee_type = '1'
      deposit.push(data)
    }
    this.ruleForm.deposit_info = deposit

    this.upinfo()
    // 获取商户提现费率
    if (this.data.channel_fees.withdraw.indexOf('元') != -1) {
      this.ruleForm.withdraw_info.fee_type = '2'
    }
    this.ruleForm.withdraw_info.value = this.data.channel_fees.withdraw.replace(/\s+|%\/笔|元\/笔/g, "")
    this.ruleForm.withdraw_info.cost_type = this.data.channel_fees.cost_type
    // console.warn(this.data)
  },



  methods: {
    submitForm (formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          console.warn(this.ruleForm)
          for (let i = 0; i < this.ruleForm.deposit_info.length; i++) {
            if (isNaN(this.ruleForm.deposit_info[i].value) || this.ruleForm.deposit_info[i].value <= 0 || this.ruleForm.deposit_info[i].value > 99) {
              this.$message.error('充值费率必须为数字且大于0小于99');
              return
            }
          }
          if (isNaN(this.ruleForm.withdraw_info.value) || this.ruleForm.withdraw_info.value <= 0) {
            this.$message.error('提现费率必须为数字且大于0小于99');
            return
          }
          this.edit()

        } else {
          console.log('error submit!!');
          return false;
        }
      });
    },
    async edit () {
      let res = await feeEdit(this.ruleForm)
      if (res) {
        this.$message({
          message: '修改成功',
          type: 'success'
        });
        setTimeout(() => {
          this.$router.go(-1)
        }, 1000)
      }
    },
    removeDomain (item) {
      var index = this.ruleForm.deposit_info.indexOf(item)
      if (index !== -1) {
        this.ruleForm.deposit_info.splice(index, 1)
      }
      this.upinfo()
    },
    addDomain () {
      this.ruleForm.deposit_info.push({
        value: '',
        fee_type: '1',
        key: Date.now()
      });
      this.upinfo()
    },
    // 更新充值费率列表
    upinfo () {
      for (let i = 0; i < this.payment_methods.length; i++) {
        this.payment_methods[i].disabled = false
      }

      for (let i = 0; i < this.payment_methods.length; i++) {
        for (let j = 0; j < this.ruleForm.deposit_info.length; j++) {
          if (this.payment_methods[i].value == this.ruleForm.deposit_info[j].name) {
            this.payment_methods[i].disabled = true
          }
        }
      }
    }
  },
}
</script>

<style lang="less">
@import "../../style/mixin";
#editormerchant {
  h4 {
    width: 82%;
    margin: auto;
    padding: 10px;
    margin-bottom: 20px;
    border-bottom: 1px solid #ddd;
  }
  .main {
    .demo-ruleForm {
      width: 600px;
      margin: auto;
    }
    .error-left {
      .el-form-item__error {
        left: 54%;
      }
    }
  }
  .merchantInfo {
    padding: 10px 20px;
    ul {
      width: 82%;
      margin: auto;
      padding-bottom: 20px;
      li {
        display: inline-block;
        width: 33%;
        line-height: 40px;
        font-size: 16px;
      }
    }
  }
}
</style>