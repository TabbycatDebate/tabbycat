module.exports = {
  plugins: ['lodash'],
  presets: [
    ['@vue/cli-plugin-babel/preset', {
      polyfills: [
        // 'es6.promise',
        // 'es6.symbol',
        // 'es6.array',
      ],
    }],
  ],
};
