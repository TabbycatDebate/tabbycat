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

gulp.task('js-admin-vendor-compile', function() {
  gulp.src(['bower_components/jquery/dist/jquery.js',
            'bower_components/bootstrap-sass/assets/javascripts/bootstrap.js',
            'templates/js/vendor/jquery.dataTables.js',
            'templates/js/vendor/fixed-header.js',
            'bower_components/vue/dist/vue.js'
          ])
  .pipe(concat('vendor-admin.js'))
  .pipe(uglify())
  .pipe(rename(function (path) {
    path.basename += ".min";
  }))
  .pipe(rename({dirname: ''})) // Remove folder structure
  .pipe(gulp.dest('static/js/vendor/'));
});

gulp.task('js-public-vendor-compile', function() {
  gulp.src(['bower_components/vue/dist/vue.js',
            'bower_components/vue-strap/dist/vue-strap.js',])
  .pipe(concat('vendor-public.js'))
  .pipe(uglify())
  .pipe(rename(function (path) {
    path.basename += ".min";
  }))
  .pipe(rename({dirname: ''})) // Remove folder structure
  .pipe(gulp.dest('static/js/vendor/'));
});

// Creates task for collecting optional dependencies (loaded per page)
gulp.task('js-optional-vendor-compile', function() {
  gulp.src(['bower_components/jquery/dist/jquery.min.js', // Redundant but needed for debug toolbar
            'bower_components/d3/d3.min.js',
            'bower_components/jquery-ui/jquery-ui.min.js',
            'bower_components/jquery-validation/dist/jquery.validate.min.js',
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
gulp.task('build', [
                    'fonts-compile',
                    'styles-compile',
                    'js-compile',
                    'js-admin-vendor-compile',
                    'js-public-vendor-compile',
                    'js-optional-vendor-compile'
                   ]);