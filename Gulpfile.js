var gulp = require('gulp');

// Compilation
var sass = require('gulp-sass');
var rename = require('gulp-rename');

// Compression
var minifyCSS = require('gulp-minify-css');
var uglify = require('gulp-uglify');
var gzip = require('gulp-gzip');
var gzip_options = {
    threshold: '1kb',
    gzipOptions: {
        level: 9
    }
};

// Local Dev
// var livereload = require('gulp-livereload'); TODO see http://www.revsys.com/blog/2014/oct/21/ultimate-front-end-development-setup/

// Creates task for compiling SCSS
gulp.task('styles-compile', function() {
  gulp.src('static/scss/*.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('staticfiles/css/'));
});

gulp.task('styles-compress', ['styles-compile'], function() {
  return gulp.src('staticfiles/css/*.css')
  .pipe(minifyCSS())
  .pipe(rename(function (path) {
    path.basename += ".min";
  }))
  .pipe(gulp.dest('staticfiles/css/'));
});

// Creates task for compiling fonts
gulp.task('fonts-compile', function() {
  gulp.src([
      'bower_components/**/*.eot',
      'bower_components/**/*.svg',
      'bower_components/**/*.ttf',
      'bower_components/**/*.woff',
      'bower_components/**/*.woff2',
    ])
    .pipe(rename({dirname: ''})) // Remove folder structure
    .pipe(gulp.dest('staticfiles/fonts/vendor/'));
});

// Creates task for collecting dependencies
gulp.task('js-dependencies', function() {
  gulp.src(['bower_components/**/dist/**/*.js',
            'bower_components/boostrap-sass/assets/javascripts/*.js',
            'bower_components/datatables.net/js/*.js',
            'bower_components/datatables-fixedheader/js/*.js',
            'bower_components/d3/*.js',
            'bower_components/jquery-ui/*.js',
          ])
    .pipe(rename({dirname: ''})) // Remove folder structure
    .pipe(gulp.dest('staticfiles/js/vendor/'));
});

// TODO: concatenate JS before compressing

gulp.task('js-compress', ['js-dependencies'], function() {
  return gulp.src('static/js/*.js')
    .pipe(uglify())
    .pipe(rename(function (path) {
      path.basename += ".min";
    }))
    .pipe(gulp.dest('staticfiles/js/'));
});

// Automatically trigger the styles task when a file changes when `gulp` is running
gulp.task('default',function() {
    gulp.watch('static/scss/**/*.scss', ['styles-compile', 'styles-compress']);
});