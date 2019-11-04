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
		// baseUrl = 'http://192.168.137.138:6082/api/merchantoffice/v1';
		// baseUrl = 'http://192.168.0.109:8080/api/merchantoffice/v1';
		baseUrl = "https://merchantoffice.epay1001.com/api/merchantoffice/v1"
		break;
	case 'testing': //测试环境
		baseUrl = "https://" + window.location.host + "/api/merchantoffice/v1"
		break;
	case 'production': //生产环境
		baseUrl = "https://" + window.location.host + "/api/merchantoffice/v1"
		break;
}

export {
	baseUrl,
	routerMode,
	baseImgPath
}