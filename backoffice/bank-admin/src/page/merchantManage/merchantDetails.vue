<template>
  <main class="fillcontain">
    <!-- 订单信息 -->
    <section class="orderInfo">
      <div class="orderbox" v-if="data">
        <ul></ul>
        <h4>基本信息</h4>
        <ul>
          <li>
            商户编号：<span> {{ data.id }}</span>
          </li>
          <li>
            商户名称：<span>{{ data.name }}</span>
          </li>
          <li>
            商户类型：<span> {{ data.type }}</span>
          </li>
          <li>域名：<span class="domains" v-html="data.domains"> </span></li>
          <li>
            总金额：<span> {{ data.balance_total | NumFormat }}</span>
          </li>
          <li>
            可用余额：<span> {{ data.balance_available | NumFormat }}</span>
          </li>
          <li>
            在途余额：<span> {{ data.balance_income | NumFormat }}</span>
          </li>
          <li>
            冻结余额：<span> {{ data.balance_frozen | NumFormat }}</span>
          </li>
        </ul>
        <h4>费率信息</h4>
        <ul>
          <li v-for="(item, index) in data.channel_fees.deposit" :key="index">
            {{ item.desc }}：<span> {{ item.rate }}</span>
          </li>
          <li>
            提现：<span>{{ data.channel_fees.withdraw }}</span>
          </li>
        </ul>
      </div>
    </section>
  </main>
</template>

<script >

export default {
  data () {
    return {
      data: null,
    }
  },

  activated () {

    if (this.$route.params.data) {
      this.data = this.$route.params.data
    } else {
      this.$router.go(-1)
    }
    console.warn(this.$route.params.data)
  },
  methods: {

  },
}
</script>

<style lang="less" scoped>
@import "../../style/mixin";
.fillcontain {
  background: #f4f4f4;

  .orderInfo {
    background: #fff;
    margin: 20px;
    h3 {
      padding: 10px 20px;
      border-bottom: 1px solid #ddd;
    }
    .orderbox {
      padding: 10px 20px;
      ul {
        padding-bottom: 20px;
        li {
          display: inline-block;
          width: 33%;
          line-height: 40px;
          font-size: 14px;
        }
        .domains {
          display: inline-block;
          width: 50px;
          vertical-align: top;
        }
      }
    }
  }
}
</style>


