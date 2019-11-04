import {
  AREA_CODA,
  SHOWLOADING,
  HIDELOADING,
  KEYBOARD,
} from './mutation-types.js'


export default {
  // 当前区号
  [AREA_CODA](state, data) {
    state.areaCode = data;
  },
  [SHOWLOADING](state) {
    state.loading = true
  },
  [HIDELOADING](state) {
    state.loading = false
  },
  [KEYBOARD](state, data) {
    state.keyboard = data
  },
}
