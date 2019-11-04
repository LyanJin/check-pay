<template>
  <main class="fillcontain clear">
    <section class="main">
      <div class="form_contianer">
        <el-form :model="registerForm" :rules="rules" ref="registerForm">
          <el-form-item prop="ori_password">
            <el-input
              placeholder="旧密码"
              v-model="registerForm.ori_password"
              maxlength="30"
              show-password
            ></el-input>
          </el-form-item>

          <el-form-item prop="new_password">
            <el-input
              placeholder="新密码"
              v-model="registerForm.new_password"
              maxlength="30"
              show-password
            ></el-input>
          </el-form-item>

          <el-form-item
            prop="new_password2"
            :rules="[
              { required: true, message: '请确认密码', trigger: 'blur' },
              { validator: vali_new_password, trigger: 'blur' }
            ]"
          >
            <el-input
              placeholder="确认新密码"
              v-model="registerForm.new_password2"
              maxlength="30"
              show-password
            ></el-input>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              @click="submitForm('registerForm')"
              class="submit_btn"
              >确认</el-button
            >
          </el-form-item>
        </el-form>
      </div>
    </section>
  </main>
</template>

<script>
import { passwordReset } from '@/api/getData'
import md5 from 'js-md5'
import { removeStore } from '@/config/mUtils'

export default {
  data () {
    return {
      registerForm: {
        ori_password: null,
        new_password: null,
        new_password2: null
      },
      rules: {
        ori_password: [
          { required: true, message: '请输入旧密码', trigger: 'blur' }
        ],
        new_password: [
          { required: true, message: '请输入新密码', trigger: 'blur' },
          { min: 6, message: '密码长度至少6位', trigger: 'blur' },
          {            validator (rule, value, callback) {
              // 验证规则密码必须包含数字和字母
              var reg = /^(?![^a-zA-Z]+$)(?!\D+$)/
              if (reg.test(value)) {
                callback()
              } else {
                callback(new Error('密码必须包含数字和字母'))
              }
            },
            trigger: 'blur'
          }
        ],
      },
    }
  },
  mounted () {

  },
  methods: {

    async submitForm (formName) {
      this.$refs[formName].validate(async (valid) => {
        if (valid) {
          const res = await passwordReset({ "ori_password": md5(this.registerForm.ori_password), "new_password": md5(this.registerForm.new_password) })
          if (res) {
            this.$message({
              type: 'success',
              message: '修改成功请重新登录'
            });
            removeStore('token')
            setTimeout(() => {
              this.$router.push('/')
            }, 1000)
          }
        }
      });
    },
    vali_new_password (rule, value, callback) {
      if (this.registerForm.new_password && value == this.registerForm.new_password) {
        callback()
      } else {
        callback(new Error('新密码不一致'))
      }
    },
  },
}
</script>

<style lang="less" scoped>
@import "../../style/mixin";
.login_page {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  background-color: #324057;
}
.manage_tip {
  position: absolute;
  width: 100%;
  top: -100px;
  left: 0;
  p {
    font-size: 34px;
    color: #fff;
  }
}
.form_contianer {
  width: 320px;
  .lr();
  padding: 25px;
  margin-top: 40px;
  border-radius: 5px;
  text-align: center;
  background-color: #f4f4f4;
  .submit_btn {
    width: 100%;
    font-size: 16px;
  }
}
.form-fade-enter-active,
.form-fade-leave-active {
  transition: all 1s;
}
.form-fade-enter,
.form-fade-leave-active {
  transform: translate3d(0, -50px, 0);
  opacity: 0;
}
</style>
