var gulp = require('gulp');
var gutil = require('gulp-util'); // Error logging + NoOop

// Compilation
var sass = require('gulp-sass');
var rename = require('gulp-rename');
var concat = require('gulp-concat');

// Compression
var cleanCSS = require('gulp-clean-css');
var uglify = require('gulp-uglify');

// Browserify
var browserify = require('browserify'); // Bundling modules
var babelify = require('babelify'); // Use ES syntax
var vueify = require('vueify');
var source = require('vinyl-source-stream'); // Use browserify in gulp
var es = require('event-stream'); // Browserify multiple files at once
var streamify = require('gulp-streamify');

// Config
var outputDir = 'tabbycat/static/';
var isProduction = (gutil.env.production === true) ? true: false;

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
    .pipe(gulp.dest(outputDir + 'fonts/'));
});

gulp.task('styles-compile', function() {
  gulp.src([
      'tabbycat/templates/scss/printables.scss',
      'tabbycat/templates/scss/style.scss'])
    .pipe(sass().on('error', sass.logError))
    // '*' compatability = IE9+
    .pipe(isProduction ? cleanCSS({compatibility: '*'}) : gutil.noop())
    .pipe(gulp.dest(outputDir + '/css/'));
});

gulp.task("js-compile", function() {

  gulp.src([
    'tabbycat/templates/js-standalones/*.js',
    ])
    .pipe(isProduction ? uglify() : gutil.noop())
    .pipe(gulp.dest(outputDir + '/js/'));

  gulp.src([
    'node_modules/datatables.net/js/jquery.dataTables.js', // Deprecate,
    'node_modules/jquery-validation/dist/jquery.validate.js', // Deprecate,
    'tabbycat/templates/js-vendor/*.js', // Deprecate,
    ])
    .pipe(isProduction ? uglify() : gutil.noop())
    .pipe(gulp.dest(outputDir + '/js/vendor/'));

  // With thanks to https://fettblog.eu/gulp-browserify-multiple-bundles/
  // We define our input files, which we want to have bundled
  var files = [
      'tabbycat/templates/js-bundles/main.js',
      'tabbycat/templates/js-bundles/tournament-home.js',
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
      .pipe(isProduction ? streamify(uglify()) : gutil.noop())
      .pipe(rename({
          extname: '.bundle.js',
          dirname: ''
      }))
      .pipe(gulp.dest(outputDir + '/js/'))
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

