<template>
  <div class="login_page">
    <transition name="form-fade" mode="in-out">
      <section class="form_contianer" v-show="showLogin">
        <div class="manage_tip">
          <p>商户后台管理系统</p>
        </div>
        <el-form :model="loginForm" :rules="rules" ref="loginForm">
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              maxlength="10"
              placeholder="用户名"
              ><span>dsfsf</span></el-input
            >
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              placeholder="请输入密码"
              v-model="loginForm.password"
              maxlength="30"
              show-password
            ></el-input>
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              @click="submitForm('loginForm')"
              class="submit_btn"
              >登录</el-button
            >
          </el-form-item>
        </el-form>
      </section>
    </transition>
  </div>
</template>

<script>
import { login } from '@/api/getData'
import md5 from 'js-md5'
import { setSessStore } from '@/config/mUtils'

export default {
  data () {
    return {
      loginForm: {
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
  computed: {

  },
  methods: {

    async submitForm (formName) {
      this.$refs[formName].validate(async (valid) => {
        if (valid) {
          const res = await login({ "account": this.loginForm.username, "password": md5(this.loginForm.password) })
          if (res) {
            this.$message({
              type: 'success',
              message: '登录成功'
            });
            // 成功更新token
            setSessStore('token', res.data.token)
            // 成功保存用户名
            setSessStore('username', this.loginForm.username)
            this.$router.push('manage')
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
  background-color: #fff;
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
