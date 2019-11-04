<template>
  <main class="main">
    <header-top headTitle="交易记录">
      <span slot="screening" class="screening" @click="screen">筛选</span>
    </header-top>
    <div class="time border-bottom" @click="timeScreen">
      {{ params.year }}年 {{ params.mouth }}月
      <i class="iconfont  icon-unfold"></i>
    </div>

    <van-pull-refresh v-model="isLoading" @refresh="onRefresh">
      <!-- 交易记录 -->
      <van-list
        v-model="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <section v-if="orderDate && orderDate.length > 0">
          <ul class="list">
            <li
              class="details border-bottom"
              v-for="(item, index) in orderDate"
              :key="index"
              @click="info(item)"
            >
              <div>
                <p class="text">{{ item.order_type }}</p>
                <span>{{ item.create_time }}</span>
              </div>
              <div class="moneybox">
                <p
                  v-if="item.order_type"
                  :class="{ money: Number(item.amount) > 0 }"
                >
                  {{ item.amount | NumFormat }}
                </p>
                <span>
                  {{ item.status }}
                </span>
              </div>
            </li>
          </ul>
        </section>
        <div class="noRecord" v-else>
          <img src="../../assets/image/noRecord.png" alt="" />
          <p>暂无交易记录</p>
        </div>
      </van-list>
    </van-pull-refresh>

    <!-- 筛选 -->
    <screening
      :show="show"
      @hide="
        () => {
          show = false;
        }
      "
      @getItem="getItem"
    ></screening>

    <van-popup v-model="timeShow" position="bottom" :overlay="true">
      <van-datetime-picker
        v-model="currentDate"
        type="year-month"
        :min-date="minDate"
        :max-date="maxDate"
        :formatter="formatter"
        @cancel="timeScreen"
        @confirm="onConfirm"
      />
    </van-popup>
    <div class="bg"></div>
  </main>
</template>

<script>
import { DatetimePicker, Popup, List, PullRefresh } from 'vant';
import headerTop from '../../components/head'
import screening from '../../components/screening'
import { fail } from 'assert';
import { orderlist } from '@/api/getData'
import { mapMutations } from 'vuex'

export default {
  name: 'tradingRecord',
  data () {
    return {
      orderDate: null,  //订单列表
      loading: false,
      finished: false,
      maxDate: new Date(),  //当前时间
      minDate: new Date(new Date().getFullYear(), new Date().getMonth() - 5),  //至过去6个月
      currentDate: new Date(),
      show: false,    //显示筛选
      timeShow: false, //筛选历史时间
      isLoading: false,//下拉刷新loding
      params: {
        year: new Date().getFullYear(),
        mouth: (new Date().getMonth() + 1),
        page_index: 1, //当前N页
        payment_type: "0"  //0：全部，1：充值， 2：提现
      }
    }
  },
  components: {
    [DatetimePicker.name]: DatetimePicker,
    [Popup.name]: Popup,
    [List.name]: List,
    [PullRefresh.name]: PullRefresh,
    headerTop,
    screening
  },
  methods: {
    ...mapMutations([
      'SHOWLOADING', 'HIDELOADING'
    ]),
    // 下拉刷新更新数据
    async getOrderlist () {
      this.SHOWLOADING()
      console.warn('getOrderlist')
      // 重置翻页
      this.finished = false
      this.params.page_index = 1
      let data = await orderlist(this.params)
      if (data && data.data.order_entry_list.length > 0) {
        this.orderDate = data.data.order_entry_list
      } else {
        this.orderDate = null
      }

      this.isLoading = false;
      this.HIDELOADING()
    },
    // 显示筛选
    screen () {
      this.show = !this.show
    },
    // 点击执行筛选
    getItem (index) {
      this.params.payment_type = String(index)
      this.getOrderlist()
    },
    formatter (type, value) {
      if (type === 'year') {
        return `${value}年`;
      } else if (type === 'month') {
        return `${value}月`
      }
      return value;
    },
    //下拉刷新
    onRefresh () {
      setTimeout(() => {
        this.getOrderlist()
      }, 500);
    },
    // 显示时间选择器
    timeScreen () {
      this.timeShow = !this.timeShow
    },
    // 时间选择器选择年月
    onConfirm (data) {
      this.params.year = data.getFullYear()
      this.params.mouth = data.getMonth() + 1
      this.getOrderlist()
      this.timeScreen()
    },
    // 下拉加载更多
    async onLoad () {
      this.SHOWLOADING()
      if (this.orderDate) {
        this.params.page_index++
      }
      // 异步更新数据
      const data = await orderlist(this.params)
      if (data) {
        if (this.orderDate) {
          // 数据全部加载完成
          if (this.orderDate.length >= data.data.order_entry_total) {
            this.finished = true
          } else {
            this.orderDate = this.orderDate.concat(data.data.order_entry_list)
          }
        } else {
          this.orderDate = data.data.order_entry_list
        }
      }
      this.HIDELOADING()
      // 加载状态结束
      this.loading = false
    },
    // 查看订单详情
    info (data) {
      this.$router.push({ name: 'orderInfo', params: { data } })
    }
  }
}
</script>

<style scoped lang="scss">
@import "../../style/mixin";
.main {
  padding-top: 0.92rem;
  .time {
    height: 0.9rem;
    line-height: 0.9rem;
    background: #f6f6f6;
    font-size: 0.3rem;
    color: #888;
    padding: 0 0.3rem;
    position: fixed;
    z-index: 1;
    width: 100%;
    i {
      color: #888;
      font-size: 0.4rem;
      vertical-align: middle;
    }
  }
  .list {
    margin-top: 0.9rem;
    li {
      padding: 0 0.3rem;
      height: 1.1rem;
      display: flex;
      align-items: center;
    }

    .details {
      background: #fff;
      div {
        width: 49%;
        display: inline-block;
        p {
          font-size: 0.32rem;
        }
        span {
          font-size: 0.24rem;
          color: #888;
        }
      }

      .moneybox {
        text-align: right;
        p::before {
          content: "-";
          display: inline-block;
          line-height: 0.4rem;
          vertical-align: top;
        }
        .money {
          color: #e08c00;
          &:before {
            content: "+";
          }
        }
      }
    }
  }
  .screening {
    float: right;
    width: 1.2rem;
    height: 0.92rem;
    font-size: 0.3rem;
    color: #fff;
    line-height: 0.92rem;
    text-align: center;
  }
  .noRecord {
    text-align: center;
    @include center();
    top: 35%;
    img {
      width: 2.3rem;
    }
    p {
      color: #bbb;
      font-size: 0.28rem;
    }
  }
  .bg {
    background: #f6f6f6;
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    z-index: -1;
  }
  .van-list {
    min-height: 90vh;
  }
}
</style>
