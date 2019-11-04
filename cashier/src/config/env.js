/**
 * 配置编译环境和线上环境之间的切换
 * 
 * baseUrl: 域名地址
 * routerMode: 路由模式
 * imgBaseUrl: 图片所在域名地址
 * 
 */

let baseUrl = '';
let routerMode = 'hash'; //hash , history
let imgBaseUrl = '';

switch (process.env.NODE_ENV) {
  case 'development': //开发环境
    // baseUrl = "http://192.168.1.9:8080/api/cashier/v1"
    baseUrl = "https://cashier-test.epay1001.com/api/cashier/v1"
    // baseUrl = "http://192.168.1.5:6082/api/cashier/v1"
    break;
  case 'testing': //测试环境
    baseUrl = "https://" + window.location.host + "/api/cashier/v1"
    // baseUrl = "https://cashier-test.epay1001.com/api/cashier/v1"
    break;
  case 'production': //生产环境
    baseUrl = "https://" + window.location.host + "/api/cashier/v1"
    // baseUrl = "https://cashier-test.epay1001.com/api/cashier/v1"
    break;
}

export {
  baseUrl,
  routerMode,
  imgBaseUrl,
}
