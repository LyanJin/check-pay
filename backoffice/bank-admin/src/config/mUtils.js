/**
 * 存储localStorage
 */
export const setLocalStore = (name, content) => {
    if (!name) return;
    if (typeof content !== 'string') {
        content = JSON.stringify(content);
    }

    window.localStorage.setItem(name, content);
}

/**
 * 获取localStorage
 */
export const getLocalStore = name => {
    if (!name) return;
    let data = window.localStorage.getItem(name)
    if (data && data.indexOf('{') == -1 && data.indexOf('}') == -1) {
        return data;
    } else {
        return JSON.parse(data)
    }
}

/**
 * 存储sessStorage
 */
export const setSessStore = (name, content) => {
    if (!name) return;
    if (typeof content !== 'string') {
        content = JSON.stringify(content);
    }

    window.sessionStorage.setItem(name, content);
}


/**
 * 获取sessStorage
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
 * 删除localStorage
 */
export const removeStore = name => {
    if (!name) return;
    window.localStorage.removeItem(name);
    window.sessionStorage.removeItem(name);
}
/**
 * 时间格式转换
 */
export const getTimeForm = data => {
    let Y = data.getFullYear() + '-';
    let M = (data.getMonth() + 1 < 10 ? '0' + (data.getMonth() + 1) : data.getMonth() + 1) + '-';
    let D = data.getDate() + ' ';
    let h = data.getHours() + ':';
    let m = data.getMinutes() + ':';
    let s = data.getSeconds();
    return Y + M + D + h + m + s
}