import Vue from 'vue'
import Vuex from 'vuex'
import mutations from './mutations'
// import actions from './action'
// import getters from './getters'

Vue.use(Vuex)

const state = {
  //区号
  areaCode: {
    cn: '中国大陆',
    phone_code: '+86'
  },
  loading: false,
  //键盘数字
  keyboard: ''
}

export default new Vuex.Store({
  state,
  // getters,
  // actions,
  mutations,
})
