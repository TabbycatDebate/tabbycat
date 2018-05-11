var gulp = require('gulp');
var gutil = require('gulp-util'); // Error logging + NoOop

// Compilation
var sass = require('gulp-sass');
var rename = require('gulp-rename');
var concat = require('gulp-concat');
var envify = require('envify');

// Compression
var cleanCSS = require('gulp-clean-css');
var uglify = require('gulp-uglify-es').default;
var sourcemaps  = require('gulp-sourcemaps'); // Make source maps
var buffer = require('vinyl-buffer'); // Need to convert stream back for maps

// Browserify
var browserify = require('browserify'); // Bundling modules
var watchify = require('watchify'); // Incremental Browserify
// var hotmodulereload = require('browserify-hmr');
var babelify = require('babelify'); // Use ES syntax
var vueify = require('vueify');
var source = require('vinyl-source-stream'); // Use browserify in gulp
var es = require('event-stream'); // Browserify multiple files at once
var streamify = require('gulp-streamify');

// Debug & Config
var livereload = require('gulp-livereload');
var outputDir = 'tabbycat/static/';

var isProduction = (process.env.NODE_ENV === 'production') ? true : false;
if (isProduction === true) {
  console.log('GULP: Building for production');
} else if (isProduction === false) {
  console.log('GULP: Building for development');
}

// Browserify bundle sequence
function bundle(entry, incremental, i) {

  // If build-ing just use browserify
  var bundleFunction = browserify({
    noparse: ['jquery', 'lodash'], // Skip big libs
    fast: true, // Skip detecting/inserting global vars
  });

  // If watch-ing wrap with watchify
  if (incremental === true) {
    bundleFunction = watchify(bundleFunction)
      // This should work with webpack; but doesn't seem to without it
      // .plugin(hotmodulereload, {
      //   // We have both admin and public instances; so can't run two HMRs on
      //   // the same socket; hence using the index to increment the key/ports
      //   // to prevent collision
      //   key: i,
      //   port: 3123 + i,
      // });
  }

  return bundleFunction
    .add(entry)
    .on('update', function() {
      if (incremental === true) {
        bundle(entry, true);
        console.log('[        ] Finished rebundling via watchify');
      }
    })
    .transform(vueify).on('error', gutil.log)
    .transform([babelify, {
      presets: ["es2015"],
      plugins: ['transform-runtime']
    }]).on('error', gutil.log)
    .transform(envify, {
      // Read from the gulp --production flag to determine whether Vue
      // should be in development mode or not
      global: true,
      _: 'purge',
    }).on('error', gutil.log)
    .bundle().on('error', gutil.log)
      .on('error', function() {
        gutil.log
        this.emit('end');
      })
    .pipe(source(entry)).on('error', gutil.log)
    // Convert the stream back to to a buffer
    .pipe(buffer())
    // Save the source map if in development
    .pipe(!isProduction ? sourcemaps.init({loadMaps: true}) : gutil.noop())
    // Compress the source if on production
    .pipe(isProduction ? uglify() : gutil.noop()).on('error', gutil.log)
    // Restore the sourcemap if in development
    .pipe(!isProduction ? sourcemaps.write() : gutil.noop())
    // Rename and move the file
    .pipe(rename({ extname: '.bundle.js', dirname: '' }))
    .pipe(gulp.dest(outputDir + '/js/'))
}

// Tasks
gulp.task('fonts-compile', function() {
  gulp.src([
      'node_modules/inter-ui/Inter UI (web)/*.woff',
      'node_modules/inter-ui/Inter UI (web)/*.woff2',
    ])
    .pipe(gulp.dest(outputDir + 'fonts/'));
});

gulp.task('styles-compile', function() {
  gulp.src([
      'tabbycat/templates/scss/allocation-old.scss',
      'tabbycat/templates/scss/printables.scss',
      'tabbycat/templates/scss/style.scss'])
    .pipe(sass().on('error', sass.logError))
    // '*' compatability = IE9+
    .pipe(isProduction ? cleanCSS({compatibility: '*'}) : gutil.noop())
    .pipe(gulp.dest(outputDir + '/css/'))
    .pipe(isProduction ? gutil.noop() : livereload());
});

// Tasks
gulp.task('jsi18n-compile', function() {
  // AR
  gulp.src(['tabbycat/locale/jsi18n/ar/djangojs.js'])
    .pipe(isProduction ? uglify() : gutil.noop())
    .pipe(gulp.dest(outputDir + '/jsi18n/ar/'))
  // FR
  gulp.src(['tabbycat/locale/jsi18n/fr/djangojs.js'])
    .pipe(isProduction ? uglify() : gutil.noop())
    .pipe(gulp.dest(outputDir + '/jsi18n/fr/'))
  // EN
  gulp.src(['tabbycat/locale/jsi18n/en/djangojs.js'])
    .pipe(isProduction ? uglify() : gutil.noop())
    .pipe(gulp.dest(outputDir + '/jsi18n/en/'))
  // ES
  gulp.src(['tabbycat/locale/jsi18n/es/djangojs.js'])
    .pipe(isProduction ? uglify() : gutil.noop())
    .pipe(gulp.dest(outputDir + '/jsi18n/es/'))
  // JA
  gulp.src(['tabbycat/locale/jsi18n/ja/djangojs.js'])
    .pipe(isProduction ? uglify() : gutil.noop())
    .pipe(gulp.dest(outputDir + '/jsi18n/ja/'))
});

gulp.task("js-compile", function() {
  // Vendors
  gulp.src([
    'node_modules/jquery/dist/jquery.js', // For Debug Toolbar
    'node_modules/jquery-validation/dist/jquery.validate.js', // Deprecate,
    'node_modules/jsbarcode/dist/barcodes/JsBarcode.code128.min.js', // Deprecate,
    ])
    .pipe(isProduction ? uglify() : gutil.noop()) // Doesnt crash
    .pipe(gulp.dest(outputDir + '/js/vendor/'));

  // Standlones
  gulp.src(['tabbycat/templates/js-standalones/*.js'])
    // Can't run uglify() until django logic is out of standalone js files
    // .pipe(isProduction ? uglify() : gutil.noop())
    .pipe(gulp.dest(outputDir + '/js/'))
    .pipe(isProduction ? gutil.noop() : livereload());
});

// With thanks to https://fettblog.eu/gulp-browserify-multiple-bundles/
// We define our input files, which we want to have bundled and then map them
// to our stream function using files.map()
var files = [
    'tabbycat/templates/js-bundles/public.js',
    'tabbycat/templates/js-bundles/admin.js'
];

gulp.task("js-browserify", function() {
  var tasks = files.map(function(entry, i) {
    return bundle(entry, false, i);
  });
  return es.merge.apply(null, tasks);
});

gulp.task("js-watchify", function() {
  var tasks = files.map(function(entry, i) {
    return bundle(entry, true, i);
  });
  return es.merge.apply(null, tasks);
});

gulp.task("html-reload", function() {
  return gulp.src('').pipe(livereload());
});

// Runs with --production if debug is false or there's no local settings
gulp.task('build', [
  'fonts-compile', 'styles-compile', 'jsi18n-compile', 'js-compile', 'js-browserify'
 ]);

// Runs when debug is True and when runserver/collectstatic is called
// Watch the CSS/JS for changes and copy over to static AND static files when done
gulp.task('watch', [
    'fonts-compile', 'styles-compile', 'jsi18n-compile', 'js-compile', 'js-watchify'
  ], function() {
    livereload.listen();
    gulp.watch('tabbycat/templates/scss/**/*.scss', ['styles-compile']);
    gulp.watch('tabbycat/templates/js-standalones/*.js', ['js-compile']);
    gulp.watch('tabbycat/**/*.html', ['html-reload']);
  }
);
