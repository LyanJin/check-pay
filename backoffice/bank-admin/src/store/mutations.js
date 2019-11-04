import {
	TITLE,
	BALANCE_EDIT,
	NEW_ORDER
} from './mutation-types.js'


export default {
	// 标题
	[TITLE](state, data) {
		state.title = data;
	},
	// 商户余额调整
	[BALANCE_EDIT](state, data) {
		state.balanceEdit = data;
	},
	// 待认领订单数
	[NEW_ORDER](state, data) {
		state.newOrder = data;
	},
}