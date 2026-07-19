// Re-export the global jQuery loaded via <script> tag in base.html.
// This ensures the Vite bundle (and Bootstrap) use the same jQuery
// instance that jquery.validate.js and other plugins attach to.
export default window.jQuery
