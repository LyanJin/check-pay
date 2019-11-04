<template>
  <main id="newmerchant">
    <section class="main">
      <el-form
        :model="ruleForm"
        :rules="rules"
        ref="ruleForm"
        label-width="120px"
        class="demo-ruleForm"
      >
        <el-form-item label="商户名称" prop="name">
          <el-select
            v-model="ruleForm.name"
            @change="recharge"
            placeholder="请选择活动区域"
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

        <el-form-item label="商户类型" prop="type">
          <el-input
            v-if="ruleForm.type == 1"
            value="普通商户"
            maxlength="20"
            readonly
          ></el-input>
          <el-input
            v-if="ruleForm.type == 2"
            value="测试商户"
            maxlength="20"
            readonly
          ></el-input>
        </el-form-item>

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
            class=" error-left"
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
              maxlength="12"
              placeholder="请输入费率"
              v-model="domain.value"
            ></el-input>
            %
            <el-button
              v-if="index > 0"
              style="margin-left:10px"
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
            maxlength="12"
            v-model="ruleForm.withdraw_info.value"
          ></el-input>
          -
          <el-select
            style="width:26%"
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
          <el-button @click="$router.go(-1)">取消</el-button>
        </el-form-item>
      </el-form>
    </section>
  </main>
</template>

<script>

import { configGetunt, feeAdd } from '@/api/getData'

export default {
  data () {
    return {
      ruleForm: {
        name: null,
        type: '1',
        deposit_info: [{
          name: '',
          value: '',
          fee_type: "1"
        }],
        withdraw_info: {
          value: '',
          fee_type: '1',
          cost_type: ''
        }
      },
      merchant_names: null,  //商户名称
      payment_methods: null, //充值方式
      rules: {
        name: [
          { required: true, message: '请输入活动名称', trigger: 'blur' },
        ],
        withdraw_info: [
          { required: true, message: '请输入提现费率', trigger: 'blur' }
        ],
      },
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
    // 初始化获取配置信息
    let res = await configGetunt()
    this.merchant_names = res.data.merchant_names
    this.payment_methods = res.data.payment_methods
    this.ruleForm = {
      name: null,
      type: '1',
      deposit_info: [{
        name: '',
        value: '',
        fee_type: "1"
      }],
      withdraw_info: {
        value: '',
        fee_type: '1'
      }
    }
  },

  methods: {
    // 提交
    async submitForm (formName) {
      console.warn(this.ruleForm)
      this.$refs[formName].validate((valid) => {
        if (valid) {
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
          this.Add()

        } else {
          console.log('error submit!!');
          return false;
        }
      });
    },
    async Add () {
      console.log(this.ruleForm);
      let res = await feeAdd(this.ruleForm)
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
    // 更新商户类型
    async recharge (data) {
      let obj = {};
      obj = this.merchant_names.find((item) => {
        console.warn(item)
        return item.name === data;
      });
      this.ruleForm.type = obj.type
      console.warn(obj)
    },
    removeDomain (item) {
      var index = this.ruleForm.deposit_info.indexOf(item)
      if (index !== -1) {
        this.ruleForm.deposit_info.splice(index, 1)
      }
    },
    addDomain () {
      this.ruleForm.deposit_info.push({
        value: '',
        fee_type: '1',
        key: Date.now()
      });
    },
    // 更新充值费率列表
    upinfo () {
      for (let i = 0; i < this.payment_methods.length; i++) {
        this.payment_methods[i].disabled = false
      }

      for (let i = 0; i < this.payment_methods.length; i++) {
        for (let j = 0; j < this.ruleForm.deposit_info.length; j++) {
          console.warn(this.payment_methods[i].value, this.ruleForm.deposit_info[j].name)
          if (this.payment_methods[i].value == this.ruleForm.deposit_info[j].name) {
            this.payment_methods[i].disabled = true
          }
        }
      }
      console.warn(this.payment_methods)
      console.warn(this.ruleForm.deposit_info)
    }

  }
}
</script>

<style lang="less" >
@import "../../style/mixin";
#newmerchant {
  .main {
    .demo-ruleForm {
      width: 600px;
      margin: auto;
    }
    .el-select {
      width: 100%;
    }
  }
  .error-left {
    .el-form-item__error {
      left: 54%;
    }
  }
}
</style>