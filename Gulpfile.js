var gulp = require('gulp');

// Compilation
var sass = require('gulp-sass');
var rename = require('gulp-rename');
var concat = require('gulp-concat');

// Compression
var minifyCSS = require('gulp-minify-css');
var uglify = require('gulp-uglify');

// Browserify
var browserify = require('browserify');
var babelify = require('babelify');
var vueify = require('vueify');
var source = require('vinyl-source-stream');
var gutil = require('gulp-util');

gulp.task('fonts-compile', function() {
  gulp.src([
      'bower_components/**/*.eot',
      'bower_components/**/*.svg',
      'bower_components/**/*.ttf',
      'bower_components/**/*.woff',
      'bower_components/**/*.woff2',
    ])
    .pipe(rename({dirname: ''})) // Remove folder structure
    .pipe(gulp.dest('tabbycat/static/fonts/vendor/'));
});

gulp.task('styles-compile', function() {
  gulp.src([
      'tabbycat/templates/scss/printables.scss',
      'tabbycat/templates/scss/style.scss'])
    .pipe(sass().on('error', sass.logError))
    .pipe(minifyCSS())
    .pipe(gulp.dest('tabbycat/static/css/'));
});

gulp.task('styles-dev', function() {
  gulp.src([
      'tabbycat/templates/scss/printables.scss',
      'tabbycat/templates/scss/style.scss'])
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('tabbycat/static/css/'))
});

// Creates task for collecting dependencies
gulp.task('js-compile', function() {
  gulp.src(['tabbycat/templates/js/*.js'])
  .pipe(uglify())
  .pipe(rename({dirname: ''})) // Remove folder structure
  .pipe(gulp.dest('tabbycat/static/js/'));
});

// Creates task for collecting dependencies
gulp.task('js-dev', function() {
  gulp.src(['tabbycat/templates/js/*.js'])
  .pipe(rename({dirname: ''})) // Remove folder structure
  .pipe(gulp.dest('tabbycat/static/js/'))
});

gulp.task('js-base-vendor-compile', function() {
  gulp.src(['bower_components/jquery/dist/jquery.js',
            'bower_components/bootstrap-sass/assets/javascripts/bootstrap.js',
            'bower_components/vue/dist/vue.js',
          ])
  .pipe(concat('vendor-base.js'))
  .pipe(uglify())
  .pipe(rename({dirname: ''})) // Remove folder structure
  .pipe(gulp.dest('tabbycat/static/js/vendor/'));
});

// Creates task for collecting optional dependencies (loaded per page)
gulp.task('js-optional-vendor-compile', function() {
  gulp.src(['tabbycat/templates/js/vendor/jquery.dataTables.js',
            'bower_components/jquery/dist/jquery.js', // Redundant but needed for debug toolbar
            'bower_components/d3/d3.js',
            'bower_components/jquery-ui/jquery-ui.js',
            'bower_components/jquery-validation/dist/jquery.validate.js',
            'bower_components/vue/dist/vue.js', // For when debug is on
          ])
  .pipe(uglify())
  .pipe(rename({dirname: ''})) // Remove folder structure
  .pipe(gulp.dest('tabbycat/static/js/vendor/'));
});


gulp.task("vue", function() {
  return browserify('./tabbycat/templates/main.js')
    .transform(vueify).on('error', gutil.log)
    .transform([babelify, {
        presets: ["es2015"],
        plugins: ['transform-runtime']
    }]).on('error', gutil.log)
    .bundle()
    .pipe(source('main.js'))
    .pipe(gulp.dest('tabbycat/static/js'))
});


// Build task for production
gulp.task('build-prod', [
  'fonts-compile',
  'styles-compile',
  'js-compile',
  'js-base-vendor-compile',
  'js-optional-vendor-compile'
 ]);

// Build task for production
gulp.task('build-dev', [
  'fonts-compile',
  'styles-dev',
  'js-dev',
  'js-base-vendor-compile',
  'js-optional-vendor-compile'
]);

// Not default runs when 'dj runserver' does
// Watch the CSS/JS for changes and copy over to static AND static files when done
gulp.task('default', ['styles-dev', 'vue'], function() {
  gulp.watch('tabbycat/templates/vue/**/*.vue', ['vue']);
  gulp.watch('tabbycat/templates/scss/**/*.scss', ['styles-dev']);
  gulp.watch('tabbycat/templates/js/**/*.js', ['js-dev']);
});

