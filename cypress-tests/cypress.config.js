const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    baseUrl: process.env.WEBTOURS_HOST || "http://127.0.0.1:1080",
    specPattern: "cypress/e2e/**/*.cy.js",
    supportFile: "cypress/support/e2e.js",
    defaultCommandTimeout: 10000,
    video: false,
    screenshotOnRunFailure: true,
    // Web Tours est une application a frames : on garde la meme origine
    chromeWebSecurity: false,
  },
  reporter: "junit",
  reporterOptions: {
    mochaFile: "reports/junit.xml",
    toConsole: false,
  },
});
