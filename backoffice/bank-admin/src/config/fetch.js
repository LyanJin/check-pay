import {
	baseUrl
} from './env'
import ElementUI from 'element-ui'
import {
	getLocalStore,
	removeStore
} from '@/config/mUtils.js'
import router from '../router'


/**
 * url   请求路径
 * data  请求参数
 * type  请求类型
 * loading   true开启  flase关闭
 * method  是否兼容
 */

let touch = true //防止多次发送请求
export default async (url = '', data = {}, loading = true, type = 'POST', method = 'fetch') => {
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
				method: type,
				headers: {
					'Accept': 'application/json',
					'Content-Type': 'application/json',
					'Authorization': getLocalStore('token') ? 'Bearer ' + getLocalStore('token') : '',
					"Access-Control-Expose-Headers": "Content-Disposition"
				},
				mode: "cors",
				cache: "force-cache"
			}

			if (type == 'POST') {
				Object.defineProperty(requestConfig, 'body', {
					value: JSON.stringify(data)
				})
			}
			let timeOut, loadingInstance = null
			try {

				// 如果0.8秒接口未响应执行loading
				if (loading) {
					timeOut = setTimeout(() => {
						loadingInstance = ElementUI.Loading.service({
							lock: true,
							text: 'Loading',
							spinner: 'el-icon-loading',
							background: 'rgba(0, 0, 0, 0.7)'
						});
						// 超时处理
						setTimeout(() => {
							if (!touch && loadingInstance) {
								console.warn('8秒后关闭loading')
								loadingInstance.close();
								touch = true
							}
						}, 8000);
					}, 800);
				}


				const response = await fetch(url, requestConfig);

				/*************************
				 * 
				 * 	检测 Content-Type是否为下载文件
				 * 
				 ************************/


				if (!response.headers.get('Content-Type').includes('application/json')) {
					response.blob().then((blob) => {
						if (loading) {
							clearTimeout(timeOut);
							if (loadingInstance) {
								loadingInstance.close();
							}
						}
						touch = true

						const a = window.document.createElement('a');
						const downUrl = window.URL.createObjectURL(blob); // 获取 blob 本地文件连接 (blob 为纯二进制对象，不能够直接保存到磁盘上)
						/**
						 * 在本地调试时由于跨域原因只能能拿到一些最基本的响应头，Content-Disposition获取不到
						 * 如果要访问其他头，则需要服务器设置Access-Control-Expose-Headers
						 * 测试环境可以正常使用
						 * @author
						 */
						const filename = response.headers.get('Content-Disposition').split('filename=')[1].split('.');
						a.href = downUrl;
						a.download = `${decodeURI(filename[0])}.${filename[1]}`;
						a.click();
						window.URL.revokeObjectURL(downUrl);


					});
				} else {
					const responseJson = await response.json();

					if (loading) {
						clearTimeout(timeOut);
						if (loadingInstance) {
							loadingInstance.close();
						}
					}

					touch = true

					// 成功返回
					if (responseJson.error_code == '200') {
						return responseJson
					}

					//token已过期
					if (responseJson.error_code == '1021' || responseJson.error_code == '1020') {
						removeStore('token')
						return ElementUI.MessageBox.confirm('登录时效已过期请重新登录！', '提示', {
							confirmButtonText: '确定',
							type: 'warning'
						}).then(() => {
							router.push({
								path: '/'
							})
						})
					}

					//您被迫退出
					if (responseJson.error_code == '1016') {
						removeStore('token')
						return ElementUI.MessageBox.alert(responseJson.message, '提示', {
							confirmButtonText: '确定',
							callback: () => {
								router.push({
									path: '/'
								})
							}
						})
					}

					// 失败返回提示
					ElementUI.Message.error({
						message: responseJson.message
					});
					return null
				}

			} catch (error) {
				clearTimeout(timeOut);
				touch = true
				if (loading) {
					if (loadingInstance) {
						loadingInstance.close();
					}
				}

				ElementUI.Message.error({
					message: '系统异常，请稍后重试!'
				});
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
			// 	let requestObj;
			// 	requestObj = new XMLHttpRequest();

			// 	let sendData = '';
			// 	if (type == 'POST') {
			// 		sendData = JSON.stringify(data);
			// 	}

			// 	requestObj.open(type, url, true);
			// 	requestObj.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
			// 	requestObj.send(sendData);

			// 	requestObj.onreadystatechange = () => {
			// 		if (requestObj.readyState == 4) {
			// 			if (requestObj.status == 200) {
			// 				let obj = requestObj.response
			// 				if (typeof obj !== 'object') {
			// 					obj = JSON.parse(obj);
			// 				}
			// 				resolve(obj)
			// 			} else {
			// 				reject(requestObj)
			// 			}
			// 		}
			// 	}
			// })
		}
	}
}