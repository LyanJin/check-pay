
<template>
  <transition name="slide">
    <div class="keyboard" v-show="show">
      <!-- 键盘区域 -->
      <div class="list clear">
        <div class="key" @touchstart="typing(num)" v-for="num in 9" :key="num">
          {{ num }}
        </div>
        <div class="keynone"></div>
        <div class="key" @touchstart="typing('0')">0</div>
        <div
          class="keynone icon-jianpan_shanchu iconfont"
          @touchstart="typing('dele')"
        ></div>
      </div>
    </div>
  </transition>
</template>

<script>
import { mapState, mapMutations } from 'vuex'

export default {
  props: {
    show: { type: Boolean, default: false },  //默认键盘是否展示
    length: { typr: Number, default: 6 }  //  输出值长度
  },
  data () {
    return {
      Number: '' // 输出值
    }
  },
  activated () {
    console.warn('kayboa')
    this.KEYBOARD('')
    this.Number = ''
  },
  created () {
    this.KEYBOARD('')
    this.Number = ''
  },
  methods: {
    ...mapMutations([
      'KEYBOARD'
    ]),
    // /*输入*/
    typing (val) {
      this.Number = this.trim(this.keyboard, '.', 'left')
      if (val === 'dele') {
        this.Number = this.Number.substring(0, this.Number.length - 1)
        this.Number = this.trim(this.Number, '.', 'right')
      } else if (this.Number.length < this.length) {
        if (val === '.') {
          if (this.Number.indexOf('.') < 0) {
            this.Number = this.Number + String(val)
          }
        } else {
          this.Number = (this.Number + String(val)).replace(
            /([0-9]+.[0-9]{2})[0-9]*/,
            '$1'
          )
        }
      }
      console.warn(this.Number)
      // 更新键盘
      this.KEYBOARD(this.Number)
    },
    /**
     * 去除字符串首尾指定字符
     *  @char  需要去除的指定符号
     *  @type  需要去除的方向  默认清楚前后  输入left删除前面的，输入right删除后面的
     */
    trim (data, char, type) {
      if (data) {
        if (char) {
          if (type === 'left') {
            return data.replace(new RegExp('^\\' + char + '+', 'g'), '')
          } else if (type === 'right') {
            return data.replace(new RegExp('\\' + char + '+$', 'g'), '')
          }
          return data.replace(
            new RegExp('^\\' + char + '+|\\' + char + '+$', 'g'),
            ''
          )
        }
        return data.replace(/^\s+|\s+$/g, '')
      } else {
        return ''
      }
    }
  },
  computed: {
    ...mapState([
      'keyboard'
    ])
  }
}
</script>

<style scoped lang="scss">
.keyboard {
  width: 100%;
  position: fixed;
  bottom: 0;
  left: 0;
  background: rgba(210, 213, 219, 0.9);
  z-index: 999;
  text-align: center;
  .list {
    padding: 1.6% 0 0 1.6%;
    .key {
      width: 31.7%;
      height: 6vh;
      line-height: 6vh;
      float: left;
      margin: 0 1.6% 1.6% 0;
      font-size: 0.6rem;
      background: #fff;
      border-radius: 0.1rem;
      box-shadow: 0 1px 0 #848688;
      &:active {
        background: rgba(255, 255, 255, 0.6);
      }
    }
    .keynone {
      width: 31.7%;
      height: 6vh;
      line-height: 6vh;
      float: left;
      font-size: 0.6rem;
      margin: 0 1.6% 1.6% 0;
      background: transparent;
    }
  }
}
</style>
