const path = require('path');

function resolve(dir) {
  return path.join(__dirname, dir)
}
module.exports = {
  configureWebpack: { // webpack 配置
    output: { // 输出重构  打包编译后的 文件名称  【模块名称.时间戳】
      filename: `[name].${new Date().getTime()}.js`,
      chunkFilename: `[name].${new Date().getTime()}.js`
    },
  },
  lintOnSave: true,
  chainWebpack: (config) => {
    config.resolve.alias
      .set('@', resolve('src'))
      .set('assets', resolve('src/assets'))
      .set('components', resolve('src/components'))
      .set('utils', resolve('utils/css'))
  }


}