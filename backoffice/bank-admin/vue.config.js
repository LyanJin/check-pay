const path = require('path');
const TerserPlugin = require('terser-webpack-plugin')

function resolve(dir) {
  return path.join(__dirname, dir)
}
module.exports = {
  configureWebpack: { // webpack 配置
    output: { // 输出重构  打包编译后的 文件名称  【模块名称.时间戳】
      filename: `[name].${new Date().getTime()}.js`,
      chunkFilename: `[name].${new Date().getTime()}.js`
    },
    optimization: {
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            compress: {
              warnings: false,
              drop_console: true,
              drop_debugger: true,
              pure_funcs: ['console.log', 'console.warn'],
            }
          }
        })
      ]
    },
  },
  lintOnSave: true,
  chainWebpack: (config) => {
    config.resolve.symlinks(true) // 修复热更新失效
    config.resolve.alias
      .set('@', resolve('src'))
      .set('assets', resolve('src/assets'))
      .set('components', resolve('src/components'))
      .set('utils', resolve('utils/css'))
    // config.module
    //   .rule("vue")
    //   .use("vue-loader")
    //   .loader("vue-loader")
    //   .tap(options =>
    //     Object.assign(options, {
    //       transformAssetUrls: {
    //         audio: "src"
    //       }
    //     })
    //   );
  },
  // css的处理
  css: {
    // 当为true时，css文件名可省略 module 默认为 false
    modules: false,
    // 是否将组件中的 CSS 提取至一个独立的 CSS 文件中,当作为一个库构建时，你也可以将其设置为 false 免得用户自己导入 CSS
    // 默认生产环境下是 true，开发环境下是 false
    extract: true,
    // 是否为 CSS 开启 source map。设置为 true 之后可能会影响构建的性能
    sourceMap: false,
    //向 CSS 相关的 loader 传递选项(支持 css-loader postcss-loader sass-loader less-loader stylus-loader)
    loaderOptions: {
      css: {},
      less: {}
    }
  }

}