/**
 * 存储sessionStorage
 */
export const setSessStore = (name, content) => {
  if (!name) return;
  if (typeof content !== 'string') {
    content = JSON.stringify(content);
  }
  window.sessionStorage.setItem(name, content);
}

/**
 * 获取sessionStorage
 */
export const getSessStore = name => {
  if (!name) return;
  let data = window.sessionStorage.getItem(name)
  if (data && data.indexOf('{') == -1 && data.indexOf('}') == -1) {
    return data;
  } else {
    return JSON.parse(data)
  }
}


/**
 * 存储localStorage
 */
export const setStore = (name, content) => {
  if (!name) return;
  if (typeof content !== 'string') {
    content = JSON.stringify(content);
  }
  window.localStorage.setItem(name, content);
}

/**
 * 获取localStorage
 */
export const getStore = name => {
  if (!name) return;
  return window.localStorage.getItem(name);
}

/**
 * 删除localStorage
 */
export const removeStore = name => {
  if (!name) return;
  window.localStorage.removeItem(name);
  window.sessionStorage.removeItem(name);
}
