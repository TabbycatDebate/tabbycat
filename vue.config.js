module.exports = {
  outputDir: './tabbycat/staticfiles/js/', // Output to standard directory
  configureWebpack: config => {
    if (process.env.NODE_ENV === 'production') {
      // mutate webpack config for production...
    } else {
      // mutate webpack config for development...
    }
  }
}