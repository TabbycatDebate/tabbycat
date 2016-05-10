var gulp = require('gulp');

// Compilation
var sass = require('gulp-sass');
var rename = require('gulp-rename');
var concat = require('gulp-concat');

// Compression
var minifyCSS = require('gulp-minify-css');
var uglify = require('gulp-uglify');


gulp.task('fonts-compile', function() {
  gulp.src([
      'bower_components/**/*.eot',
      'bower_components/**/*.svg',
      'bower_components/**/*.ttf',
      'bower_components/**/*.woff',
      'bower_components/**/*.woff2',
    ])
    .pipe(rename({dirname: ''})) // Remove folder structure
    .pipe(gulp.dest('static/fonts/vendor/'));
});

gulp.task('styles-compile', function() {
  gulp.src(['templates/scss/printables.scss', 'templates/scss/style.scss'])
    .pipe(sass().on('error', sass.logError))
    .pipe(minifyCSS())
    .pipe(rename(function (path) {
      path.basename += ".min";
    }))
    .pipe(gulp.dest('static/css/'));
});

// Creates task for collecting dependencies
gulp.task('js-compile', function() {
  gulp.src(['templates/js/*.js'])
  .pipe(uglify())
  .pipe(rename(function (path) {
    path.basename += ".min";
  }))
  .pipe(rename({dirname: ''})) // Remove folder structure
  .pipe(gulp.dest('static/js/'));
});

// Creates task for collecting dependencies
gulp.task('js-main-vendor-compile', function() {
  gulp.src(['bower_components/jquery/dist/jquery.js',
            'bower_components/bootstrap-sass/assets/javascripts/bootstrap.js',
            'bower_components/datatables.net/js/jquery.dataTables.js',
            'templates/js/vendor/fixed-header.js',
          ])
  .pipe(concat('vendor.js'))
  .pipe(uglify())
  .pipe(rename(function (path) {
    path.basename += ".min";
  }))
  .pipe(rename({dirname: ''})) // Remove folder structure
  .pipe(gulp.dest('static/js/vendor/'));
});

// Creates task for collecting dependencies
gulp.task('js-alt-vendor-compile', function() {
  gulp.src(['bower_components/jquery/dist/jquery.min.js', // Redundant but needed for debug toolbar
            'bower_components/d3/*.js',
            'bower_components/jquery-ui/*.js',
            'bower_components/jquery-validation/*.js',
            'bower_components/vue/dist/*.js',
          ])
  .pipe(uglify())
  .pipe(rename({dirname: ''})) // Remove folder structure
  .pipe(gulp.dest('static/js/vendor/'));
});

// Automatically build and watch the CSS folder for when a file changes
gulp.task('default', ['build'], function() {
  gulp.watch('templates/scss/**/*.scss', ['styles-compile']);
  gulp.watch('templates/js/**/*.js', ['js-compress']);
});

// Build task for production
gulp.task('build', ['fonts-compile', 'styles-compile', 'js-compile', 'js-main-vendor-compile', 'js-alt-vendor-compile' ]);