<template>
  <div class="header_container">
    <el-breadcrumb
      class="breadcrumb-container"
      separator-class="el-icon-arrow-right"
    >
      <el-breadcrumb-item
        v-for="(item, index) in breadList"
        :key="item.path"
        :to="item.path"
      >
        <!-- 监听title是否指定标题  如有指定标题则覆盖原有标题 -->
        {{ title && breadList.length - 1 == index ? title : item.meta.title }}
      </el-breadcrumb-item>
    </el-breadcrumb>

    <div class="right">
      <div class="avator">
        <div class="img">
          <img src="../assets/img/avator.jpg" />
          管理员：{{ name }}
        </div>
        <el-button class="exit" plain size="mini" @click="exit">退出</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { signout } from '@/api/getData'
import { baseImgPath } from '@/config/env'
import { removeStore, getLocalStore  } from '@/config/mUtils'


export default {
  props: {
    title: null
  },
  data () {
    return {
      baseImgPath,
      name,
      breadList: []
    }
  },
  mounted () {
    this.name = getLocalStore ('username')
    this.getBreadcrumb();
  },
  computed: {

  },
  methods: {
    async exit () {
      const res = await signout()
      if (res) {
        removeStore('token')
        this.$message({
          type: 'success',
          message: '退出成功'
        });
        this.$router.push('/');
      }
    },
    isHome (route) {
      return route.name === "home";
    },
    getBreadcrumb () {
      let matched = this.$route.matched;
      this.breadList = matched;
    }
  },
  watch: {
    $route () {
      this.getBreadcrumb();
    },
  },
}
</script>

<style lang="less">
@import "../style/mixin";
.breadcrumb-container {
  display: inline-block;
  font-size: 18px;
  vertical-align: middle;
}
.header_container {
  background-color: #eff2f7;
  height: 60px;
  line-height: 60px;
  padding-left: 20px;
}
.avator {
  margin-right: 37px;
  font-size: 14px;
  display: flex;
  .img {
    img {
      .wh(36px, 36px);
      border-radius: 50%;
      vertical-align: middle;
    }
  }
  .exit {
    margin: 15px 10px;
  }
}
</style>
