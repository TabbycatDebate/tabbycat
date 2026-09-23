const { defineConfig } = require('vite')
const pluginVue = require('@vitejs/plugin-vue')
const path = require('path')

const vue = pluginVue.default || pluginVue

module.exports = defineConfig(({ command }) => {
  const isBuild = command === 'build'

  const templatesRoot = path.resolve(__dirname, 'tabbycat/templates')
  const tabbycatRoot = path.resolve(__dirname, 'tabbycat')

  return {
    root: templatesRoot,
    base: isBuild ? '/static/vue/' : '/',
    plugins: [vue()],
    resolve: {
      alias: {
        vue: 'vue/dist/vue.esm-bundler.js',
        jquery: path.resolve(templatesRoot, 'js-bundles/jquery-shim.js'),
      },
    },
    server: {
      port: 8888,
      strictPort: true,
      host: true,
      cors: true,
      headers: {
        'Access-Control-Allow-Origin': '*',
      },
      fs: {
        allow: [templatesRoot, tabbycatRoot],
      },
    },
    build: {
      outDir: '../static/vue',
      emptyOutDir: true,
      sourcemap: true,
      rollupOptions: {
        input: {
          app: path.resolve(templatesRoot, 'js-bundles/main.js'),
        },
        output: {
          entryFileNames: 'js/[name].js',
          chunkFileNames: '[name].js',
          assetFileNames: 'assets/[name][extname]',
        },
      },
    },
  }
})
