module.exports = {
  plugins: ['lodash'],
  presets: [
    ['@vue/app', {
      polyfills: [
        // 'es6.promise',
        // 'es6.symbol',
        // 'es6.array',
      ],
    }],
  ],
};
