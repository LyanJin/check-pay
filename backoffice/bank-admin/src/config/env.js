/**
 * 配置编译环境和线上环境之间的切换
 * 
 * baseUrl: 域名地址
 * routerMode: 路由模式
 * baseImgPath: 图片存放地址
 * 
 */
let baseUrl = '';
let routerMode = 'hash';
let baseImgPath;

switch (process.env.NODE_ENV) {
	case 'development': //本地开发环境
		// baseUrl = 'http://192.168.137.138:6082/api/backoffice/v1';
		// baseUrl = 'http://192.168.0.105:6082/api/backoffice/v1';
		baseUrl = "https://backoffice.epay1001.com/api/backoffice/v1"
		break;
	case 'testing': //测试环境
		baseUrl = "https://" + window.location.host + "/api/backoffice/v1"
		// baseUrl = "https://backoffice.epay1001.com/api/backoffice/v1"
		break;
	case 'production': //生产环境
		baseUrl = "https://" + window.location.host + "/api/backoffice/v1"
		// baseUrl = "https://backoffice.epay1001.com/api/backoffice/v1"
		break;
}

export {
	baseUrl,
	routerMode,
	baseImgPath
}