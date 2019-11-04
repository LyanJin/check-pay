<template>
  <main id="newGuideRule">
    <section class="main">
      <el-form
        :model="channelForm"
        ref="channelForm"
        label-width="140px"
        class="demo-ruleForm"
      >
        <el-form-item label="引导编号：" prop="uid_list" v-if="channelForm.id">
          <el-input maxlength="30" v-model="channelForm.id" readonly>
          </el-input>
        </el-form-item>

        <el-form-item label="商户名称：" prop="channel_config">
          <el-select
            v-model="channelForm.merchants"
            value-key="value"
            multiple
            clearable
            placeholder="选填,默认为全部"
          >
            <el-option
              v-for="item in config.merchant_name"
              :key="item.value"
              :label="item.name"
              :value="item.name"
            >
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="用户ID：" prop="uid_list">
          <el-input
            maxlength="30"
            placeholder="选填,默认为全部"
            v-model="channelForm.uid_list"
            clearable
            @input="
              channelForm.uid_list = channelForm.uid_list.replace(
                /[^\d\,]/g,
                ''
              )
            "
          >
          </el-input>
        </el-form-item>

        <el-form-item label="接入类型：" prop="interface">
          <el-select
            v-model="channelForm.interface"
            clearable
            placeholder="请选择"
          >
            <el-option
              v-for="item in config.interfaces"
              :key="item.value"
              :label="item.name"
              :value="item.name"
            >
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="交易金额：" prop="amount_min">
          <el-form-item class=" error-left" prop="amount_max">
            <el-input
              style="width: 45.5%"
              maxlength="12"
              placeholder="请输入最小值"
              v-model="channelForm.amount_min"
              clearable
            >
            </el-input>
            ——
            <el-input
              maxlength="12"
              style="width: 45.5%"
              placeholder="请输入最大值"
              v-model="channelForm.amount_max"
              clearable
            >
            </el-input>
          </el-form-item>
        </el-form-item>

        <!-- <el-form-item label="引导方案输出：" prop="config_list">
          <el-select
            v-model="channelForm.config_list"
            value-key="value"
            multiple
            placeholder="请选择"
          >
            <el-option
              v-for="item in config.payment_types"
              :key="item.value"
              :label="item.desc"
              :value="item.value"
            >
            </el-option>
          </el-select>
        </el-form-item> -->

        <el-form-item
          v-for="(domain, index) in channelForm.config_list"
          :label="'引导方案输出' + (index + 1) + '：'"
          :key="domain.key"
          :prop="'config_list.' + index + '.payment_type'"
          :rules="{
            required: true,
            message: '请选择引导方案',
            trigger: 'blur'
          }"
        >
          <el-form-item
            :key="domain.key"
            class=" error-left"
            :prop="'config_list.' + index + '.priority'"
            :rules="{
              required: true,
              message: '请输入优先级',
              trigger: 'blur'
            }"
          >
            <el-select
              style="width:50%"
              v-model="domain.payment_type"
              placeholder="请选择引导方案"
              @change="upinfo"
            >
              <el-option
                v-for="item in config.payment_types"
                :key="item.value"
                :label="item.desc"
                :value="item.name"
                :disabled="item.disabled"
              >
              </el-option>
            </el-select>
            -
            <el-input
              style="width:25%"
              maxlength="12"
              placeholder="请输入优先级"
              v-model="domain.priority"
            ></el-input>

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
import { channelConfigGet, ruleAdd, ruleEdit } from '@/api/getData'

export default {
  data () {
    return {
      config: {},          //配置信息
      channelForm: {
        merchants: null,
        uid_list: null,
        interface: null,
        amount_min: null,
        amount_max: null,
        config_list: [{
          payment_type: '',
          priority: '',
        }],
      },
      rules: {
        // amount_min: [
        //   { required: true, message: '请输入单笔最小交易限额', trigger: 'blur' },
        //   {            validator (rule, value, callback) {
        //       var reg = /^-?\d{1,9}(?:\.\d{1,2})?$/
        //       if (reg.test(value)) {
        //         callback()
        //       } else {
        //         callback(new Error('请输入不超过2位小数的数字'))
        //       }
        //     },
        //     trigger: 'blur'
        //   }
        // ],
        // amount_max: [
        //   { required: true, message: '请输入单笔最大交易限额', trigger: 'blur' },
        //   {            validator (rule, value, callback) {
        //       var reg = /^-?\d{1,9}(?:\.\d{1,2})?$/
        //       if (reg.test(value)) {
        //         callback()
        //       } else {
        //         callback(new Error('请输入不超过2位小数的数字'))
        //       }
        //     },
        //     trigger: 'blur'
        //   }
        // ],
        // interface: [
        //   { required: true, message: '请选择接入类型', trigger: 'blur' }
        // ],
        // config_list: [
        //   { required: true, message: '请选择支持方式', trigger: 'blur' }
        // ],
      },
    }
  },
  async activated () {
    // 初始化获取配置信息
    let res = await channelConfigGet({ pay_type: 1 })
    if (res) {
      this.config = res.data
    }

    if (this.$route.query.data) {
      if (!this.$route.query.data.config_list) {
        this.$router.go(-1)
        return
      }
      console.warn(this.$route.query.data)
      this.TITLE('编辑引导规则')
      // 数据回显
      this.channelForm = this.$route.query.data
      this.channelForm.interface = this.$route.query.data.interface.name
      this.channelForm.uid_list = this.$route.query.data.uid_list.length > 0 ? this.$route.query.data.uid_list.join(',') : null
      this.upinfo()

    } else {
      // 清空数据
      this.channelForm = {
        config_list: [{
          payment_type: '',
          priority: '',
        }],
      }
    }
  },
  methods: {
    ...mapMutations([
      'TITLE'
    ]),
    // 提交
    async submitForm (formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          if (this.channelForm.amount_min && this.channelForm.amount_min != 0 && Number(this.channelForm.amount_min) >= Number(this.channelForm.amount_max)) {
            this.$message.error('交易金额最大值要大于最小值');
            this.channelForm.amount_max = null
          } else {
            this.Add(this.channelForm)
          }
        } else {
          return false;
        }
      });
    },
    async Add (data) {
      let res
      if (typeof (data.uid_list) == 'string') {
        data.uid_list = data.uid_list ? data.uid_list.split(",") : null
      }
      if (this.$route.query.data) {
        res = await ruleEdit(data)
      } else {
        res = await ruleAdd(data)
      }
      console.warn(data)
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
    // 删除引导方案
    removeDomain (item) {
      var index = this.channelForm.config_list.indexOf(item)
      if (index !== -1) {
        this.channelForm.config_list.splice(index, 1)
      }
      this.upinfo()
    },
    // 新增引导方案
    addDomain () {
      this.channelForm.config_list.push({
        priority: '',
        payment_type: '',
        key: Date.now()
      });
      this.upinfo()
    },
    // 更新引导方案列表
    upinfo () {
      for (let i = 0; i < this.config.payment_types.length; i++) {
        this.config.payment_types[i].disabled = false
      }

      for (let i = 0; i < this.config.payment_types.length; i++) {
        for (let j = 0; j < this.channelForm.config_list.length; j++) {
          console.warn(this.config.payment_types)
          console.warn(this.config.payment_types[i].name, this.channelForm.config_list[j].payment_type)
          if (this.config.payment_types[i].name == this.channelForm.config_list[j].payment_type) {
            this.config.payment_types[i].disabled = true
          }
        }
      }
      console.warn(this.config.payment_types)
      console.warn(this.channelForm.config_list)
    }
  },

  //离开当前页面
  deactivated () {
    this.TITLE(null)
  },
}
</script>

<style lang="less">
@import "../../style/mixin";
#newGuideRule {
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