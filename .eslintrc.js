module.exports = {
  "root": true,
  "env": {
    "node": true,
    "browser": true, // Browser window global variables
    "jquery": true, // jQuery global variable
  },
  "extends": [
    "plugin:vue/essential",
    // "plugin:vue/recommended" // TODO
    "@vue/standard"
  ],
  "rules": {
    "comma-dangle": [
      "error", "always-multiline"
    ], // Improve diffs
    "func-names": "off", // Conflicts with vue
    "object-shorthand": "off", // Conflicts with vue
    "no-underscore-dangle": "off", // Conflicts with vue
    // Vue-plugin lint rules
    "vue/require-v-for-key": "off", // Requires not using <template>; breaks layouts
    // Temporary; to fix
    "no-console": process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    "no-debugger": process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    "radix": "off",
  },
  "parserOptions": {
    "parser": "babel-eslint",
    "sourceType": "module",
  },
  "plugins": [
    "vue",
  ],
}
