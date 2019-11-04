<template>
  <main class="fillcontain clear">
    <section class="main">
      <div class="form_contianer">
        <div class="manage_tip">
          <p>添加管理员</p>
        </div>
        <el-form :model="registerForm" :rules="rules" ref="registerForm">
          <el-form-item prop="username">
            <el-input
              v-model="registerForm.username"
              maxlength="10"
              placeholder="用户名"
              ><span>dsfsf</span></el-input
            >
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              placeholder="请输入密码"
              v-model="registerForm.password"
              maxlength="30"
              show-password
            ></el-input>
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              @click="submitForm('registerForm')"
              class="submit_btn"
              >注册</el-button
            >
          </el-form-item>
        </el-form>
      </div>
    </section>
  </main>
</template>

<script>
import { registern } from '@/api/getData'
import md5 from 'js-md5'

export default {
  data () {
    return {
      registerForm: {
        username: '',
        password: '',
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ],
      },
      showLogin: false,
    }
  },
  mounted () {
    this.showLogin = true;

  },
  methods: {

    async submitForm (formName) {
      this.$refs[formName].validate(async (valid) => {
        if (valid) {
          const res = await registern({ "account": this.registerForm.username, "password": md5(this.registerForm.password) })
          if (res) {
            this.$message({
              type: 'success',
              message: '注册成功'
            });
          }
        } else {
          this.$notify.error({
            title: '错误',
            message: '请输入正确的用户名密码',
            offset: 100
          });
          return false;
        }
      });
    },
  },
  watch: {
    // adminInfo: function (newValue) {
    //   if (newValue.id) {
    //     this.$message({
    //       type: 'success',
    //       message: '检测到您之前登录过，将自动登录'
    //     });
    //     this.$router.push('manage')
    //   }
    // }
  }
}
</script>

<style lang="less" scoped>
@import "../style/mixin";
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
  .wh(320px, 170px);
  .ctp(320px, 170px);
  padding: 25px;
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
