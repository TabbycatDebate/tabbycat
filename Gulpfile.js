var gulp = require('gulp');

// Compilation
var sass = require('gulp-sass');
var rename = require('gulp-rename');
var concat = require('gulp-concat');

// Compression
var minifyCSS = require('gulp-minify-css');
var uglify = require('gulp-uglify');
var gutil = require('gulp-util'); // Error logging + ENV check

// Browserify
var browserify = require('browserify'); // Bundling modules
var babelify = require('babelify'); // Use ES syntax
var vueify = require('vueify');
var source = require('vinyl-source-stream'); // Use browserify in gulp
var es = require('event-stream'); // Browserify multiple files at once
var streamify = require('gulp-streamify')

// Config
var config = {
    outputDir: 'tabbycat/static/',
    production: !!gutil.env.production // !! = turns undefined to false
};

gulp.task('fonts-compile', function() {
  gulp.src([
      'node_modules/bootstrap-sass/assets/fonts/**/*.eot',
      'node_modules/bootstrap-sass/assets/fonts/**/*.svg',
      'node_modules/bootstrap-sass/assets/fonts/**/*.ttf',
      'node_modules/bootstrap-sass/assets/fonts/**/*.woff',
      'node_modules/bootstrap-sass/assets/fonts/**/*.woff2',
      'node_modules/lato-font/fonts/**/*.eot',
      'node_modules/lato-font/fonts/**/*.svg',
      'node_modules/lato-font/fonts/**/*.ttf',
      'node_modules/lato-font/fonts/**/*.woff',
      'node_modules/lato-font/fonts/**/*.woff2',
    ])
    .pipe(rename({dirname: ''})) // Remove folder structure
    .pipe(gulp.dest(config.outputDir + 'fonts/'));
});

gulp.task('styles-compile', function() {
  gulp.src([
      'tabbycat/templates/scss/printables.scss',
      'tabbycat/templates/scss/style.scss'])
    .pipe(sass().on('error', sass.logError))
    .pipe(config.production ? minifyCSS() : gutil.noop())
    .pipe(gulp.dest(config.outputDir + '/css/'));
});

gulp.task("js-compile", function() {

  gulp.src('tabbycat/templates/js-standalones/*.js')
    .pipe(gulp.dest(config.outputDir + '/js/'));

  // With thanks to https://fettblog.eu/gulp-browserify-multiple-bundles/
  // We define our input files, which we want to have bundled
  var files = [
      'tabbycat/templates/js-bundles/main.js',
      'tabbycat/templates/js-bundles/graphs.js',
      'tabbycat/templates/js-bundles/tournament-home.js'
  ];
  // map them to our stream function
  var tasks = files.map(function(entry) {
    return browserify({ entries: [entry] })
      .transform(vueify).on('error', gutil.log)
      .transform([babelify, {
          presets: ["es2015"],
          plugins: ['transform-runtime']
      }]).on('error', gutil.log)
      .bundle()
      .pipe(source(entry))
      .pipe(config.production ? streamify(uglify()) : gutil.noop())
      .pipe(rename({
          extname: '.bundle.js',
          dirname: ''
      }))
      .pipe(gulp.dest(config.outputDir + '/js/'))
  });
  // create a merged stream
  return es.merge.apply(null, tasks);

});

// Primary build task
gulp.task('build', [
  'fonts-compile',
  'styles-compile',
  'js-compile',
 ]);

// Note that default runs when 'dj runserver' does
// Watch the CSS/JS for changes and copy over to static AND static files when done
gulp.task('default', ['styles-compile', 'js-compile'], function() {
  gulp.watch('tabbycat/templates/scss/**/*.scss', ['styles-compile']);
  gulp.watch('tabbycat/templates/js*/**/*.js', ['js-compile']);
  gulp.watch('tabbycat/templates/js-vue/**/*.vue', ['js-compile']);
});

