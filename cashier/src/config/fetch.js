import {
  Toast,
  Dialog
} from 'vant';
import {
  baseUrl
} from './env'
import router from '../router'
import {
  setSessStore,
  getSessStore,
  removeStore
} from '@/config/common'
import store from '../store'
// let Base64 = require('js-base64').Base64;

/**
 * url   请求路径
 * data  请求参数
 * type  请求类型
 * loading   true开启  flase关闭
 * method  是否兼容
 */
let touch = true //防止多次发送请求
console.warn(touch)
export default async (url = '', data = {}, type = 'POST', loading = true, method = 'fetch') => {
  if (touch) {
    touch = false
    type = type.toUpperCase();
    url = baseUrl + url;

    if (type == 'GET') {
      let dataStr = ''; //数据拼接字符串
      Object.keys(data).forEach(key => {
        dataStr += key + '=' + data[key] + '&';
      })

      if (dataStr !== '') {
        dataStr = dataStr.substr(0, dataStr.lastIndexOf('&'));
        url = url + '?' + dataStr;
      }
    }

    if (window.fetch && method == 'fetch') {
      let requestConfig = {
        // credentials: 'include',   //跨域请求时是不带cookie的，添加该属性表示强制加入凭据头,请求时就会携带cookie。但是如果加上这个属性，那么服务器的Access-Control-Allow-Origin 就不能是‘*’，否则会报下面的错误。
        method: type, //允许跨域  no-cors不允许跨域
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json', // 指定提交方式为表单提交
          'Authorization': getSessStore('token') ? 'Bearer ' + getSessStore('token') : ''
        },
        mode: "cors",
        cache: "force-cache"
      }

      if (type == 'POST') {
        Object.defineProperty(requestConfig, 'body', {
          value: JSON.stringify(data)
        })
      }
      let timeOut
      try {

        if (loading) {
          // 如果0.8秒接口未响应执行loading
          timeOut = setTimeout(() => {
            store.commit('SHOWLOADING')
            setTimeout(() => {
              if (store.state.loading) {
                console.warn('8秒后关闭loading')
                touch = true
                store.commit('HIDELOADING')
              }
            }, 15000);
          }, 800);
        } else {
          touch = true
        }


        const response = await fetch(url, requestConfig);
        const responseJson = await response.json();
        // 成功返回
        if (loading) {
          clearTimeout(timeOut);
          touch = true
          store.commit('HIDELOADING')
        } else {
          touch = true
        }

        if (responseJson.error_code == '200' || responseJson.error_code == '1017') {
          return responseJson
        }

        // 验证码过期
        if (responseJson.error_code == '1008') {
          return Dialog.alert({
            message: '验证码已过期！'
          }).then(() => {
            router.push({
              name: 'login'
            })
          });
        }


        //token已过期
        if (responseJson.error_code == '1021' || responseJson.error_code == '1020') {
          removeStore('token')
          return Dialog.alert({
            message: '登录时效已过期请重新登录！'
          }).then(() => {
            router.push({
              name: 'login'
            })
          });
        }

        //账号其它地方登录
        if (responseJson.error_code == '1016') {
          removeStore('token')
          return Dialog.alert({
            message: responseJson.message
          }).then(() => {
            router.push({
              name: 'login'
            })
          });
        }


        // 账号已锁定
        if (responseJson.error_code == '3010' || responseJson.error_code == '3011') {
          return Dialog.confirm({
            message: responseJson.message + ',前往忘记密码！'
          }).then(() => {
            setSessStore('pageType', 'Forget')
            if (router.history.current.name === "forget") {
              router.push('home')
            } else {
              router.push('forget')
            }
          }).catch(() => {});
        }

        //账号其它地方登录
        if (responseJson.error_code == '4002') {
          return Dialog.alert({
            message: responseJson.message + ',前往忘记密码！'
          }).then(() => {
            router.push({
              name: 'messageCode'
            })
          });
        }

        // 失败返回提示
        Toast(responseJson.message);

        return null
      } catch (error) {
        if (loading) {
          clearTimeout(timeOut);
          touch = true
          store.commit('HIDELOADING')
        } else {
          touch = true
        }
        Toast('系统异常，请稍后重试!');
        // Toast(error);
        throw new Error(error)
      }
    } else {

      document.body.innerHTML = '<div style="width: 100%;height: 50px;font-size: 30px;text-align: center;font-weight: bold;">浏览器版本过低，暂不支持！请升级您的浏览器</div>';

      /*******************************
       * 
       *   不支持fetch，低版本暂不处理
       * 
       *******************************/

      // return new Promise((resolve, reject) => {
      //   let requestObj;
      //   if (window.XMLHttpRequest) {
      //     requestObj = new XMLHttpRequest();
      //   } else {
      //     requestObj = new ActiveXObject;
      //   }

      //   let sendData = '';
      //   if (type == 'POST') {
      //     sendData = JSON.stringify(data);
      //   }

      //   requestObj.open(type, url, true);
      //   requestObj.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
      //   // requestObj.setRequestHeader("Authorization", 'Basic ' + Base64.encode(tok));
      //   requestObj.send(sendData);

      //   requestObj.onreadystatechange = () => {
      //     if (requestObj.readyState == 4) {
      //       if (requestObj.status == 200) {
      //         let obj = requestObj.response
      //         if (typeof obj !== 'object') {
      //           obj = JSON.parse(obj);
      //         }
      //         resolve(obj)
      //       } else {
      //         reject(requestObj)
      //       }
      //     }
      //   }
      // })
    }
  }
}
