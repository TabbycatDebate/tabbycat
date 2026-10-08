import js from '@eslint/js'
import vue from 'eslint-plugin-vue'

export default [
  js.configs.recommended,
  ...vue.configs['flat/recommended'],
  {
    ignores: [
      '**/venv/**',
      '**/node_modules/**',
      '**/dist/**',
      '**/static/**',
      '**/staticfiles/**',
      '**/docs/_build/**',
      '**/*.min.js',
      '**/locale/**',
      '**/fixtures/**',
      '**/migrations/**',
      '**/.git/**',
      '**/coverage/**',
      '**/.cache/**',
      '**/.pytest_cache/**',
      '**/js-bundles/**',
    ],
  },
  {
    files: ['**/*.vue', '**/*.js'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        console: 'readonly',
        process: 'readonly',
        window: 'readonly',
        document: 'readonly',
        $: 'readonly',
        jQuery: 'readonly',
        require: 'readonly',
        module: 'readonly',
        __dirname: 'readonly',
        define: 'readonly',
      },
    },
    rules: {
      'comma-dangle': ['error', 'always-multiline'], // Improve diffs
      'func-names': 'off', // Conflicts with vue
      'object-shorthand': 'off', // Conflicts with vue
      'no-underscore-dangle': 'off', // Conflicts with vue
      // Vue-plugin lint rules
      'vue/require-v-for-key': 'off', // Requires not using <template>; breaks layouts
      'vue/require-default-prop': 'off', // Props don't always need defaults
      'vue/no-v-html': 'off', // v-html is used intentionally in this project
      'vue/no-template-shadow': 'off', // Template shadowing is acceptable in this context
      'vue/require-prop-types': 'off', // Prop types are optional in Vue 3 setup
      'vue/require-explicit-emits': 'off', // Explicit emits are optional
      // Temporary; to fix
      'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
      'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
      'radix': 'off',
      // Standard rules that need to be manually added
      'indent': ['error', 2],
      'quotes': ['error', 'single'],
      'semi': ['error', 'never'],
      'no-trailing-spaces': 'error',
      'eol-last': 'error',
      // Ignore common issues in vendor files
      'no-undef': 'off',
      'no-unused-vars': 'off',
      'no-empty': 'off',
      'no-cond-assign': 'off',
      'no-redeclare': 'off',
      'no-prototype-builtins': 'off',
      'no-useless-escape': 'off',
      'no-self-assign': 'off',
    },
  },
  {
    files: ['**/Popover.vue'],
    rules: {
      'vue/multi-word-component-names': 'off',
    },
  },
]
