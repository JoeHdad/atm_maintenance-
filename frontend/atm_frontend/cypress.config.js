const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
    // Increase timeout for commands
    defaultCommandTimeout: 10000,
    // Set viewport size
    viewportWidth: 1280,
    viewportHeight: 720,
    // Enable video recording for failed tests
    video: true,
    // Configure retries for CI
    retries: {
      runMode: 2,
      openMode: 0,
    },
    // Environment variables
    env: {
      apiUrl: 'http://localhost:8000/api', // Update with your backend URL
    },
  },
});
