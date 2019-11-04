<template>
  <main class="main">
    <header-top headTitle="选择手机归属地" :component="true">
      <section
        slot="head"
        class="head_goback iconfont icon-return"
        @click="hide()"
      ></section>
    </header-top>
    <section class="body">
      <!-- 头部搜索 -->
      <div class="header">
        <div class="search">
          <input
            v-NoEmoji
            type="text"
            placeholder="搜索国家名字或区号"
            v-model.trim="search"
          />
        </div>
      </div>
      <!-- 全球电话列表 -->
      <div class="item">
        <ul>
          <li
            class="letter clear"
            v-for="(item, index) in searchData"
            :key="index"
          >
            {{ item.type }}
            <div
              class="row border-bottom"
              v-for="(list, index) in item.data"
              :key="index"
              @click="countries(list)"
            >
              {{ list.cn }}
              <span class="right">{{ list.phone_code }}</span>
            </div>
          </li>
        </ul>
      </div>
    </section>
  </main>
</template>

<script>
import headerTop from './head';
import countrycode from '../../static/countrycode';
import { mapMutations } from 'vuex'

export default {
  data () {
    return {
      search: null,
      searchData: countrycode.data
    }
  },

  components: {
    headerTop
  },
  methods: {
    ...mapMutations([
      'AREA_CODA'
    ]),
    countries (data) {
      // 更新区号
      this.AREA_CODA(data)
      this.hide()
    },
    hide () {
      this.$emit('hide')
    }
  },
  watch: {
    search: function () {
      let data = JSON.parse(JSON.stringify(this.searchData))
      if (this.search) {
        this.searchData = data.filter((value, key) => {
          value.data = value.data.filter((value2, key) => {
            return String(value2.cn + value2.phone_code).indexOf(this.search) > -1
          })
          if (value.data.length > 0) {
            return true
          }
          return false
        })
      } else {
        this.searchData = countrycode.data
      }
    }
  }
}
</script>

<style scoped lang="scss">
@import "../style/mixin";

.main {
  padding-top: 0.92rem;
  .body {
    .header {
      padding: 0.2rem 0.3rem;
      position: fixed;
      width: 100%;
      background: #fff;
      z-index: 1;
      .search {
        background: #efefef;
        border-radius: 0.4rem;
        padding: 0.14rem 0.4rem;
        input {
          @include wh(90%, 0.4rem);
          line-height: 0.4rem;
          background: transparent;
          font-size: 0.3rem;
        }
      }
    }
    .item {
      padding-top: 0.9rem;
      height: 93.2vh;
      overflow: auto;
      ul {
        .letter {
          font-size: 0.3rem;
          padding: 0.3rem 0.3rem 0;
        }
        .row {
          height: 0.85rem;
          line-height: 0.85rem;
          font-size: 0.32rem;
          span {
            color: #888;
          }
        }
      }
    }
  }
}
</style>
