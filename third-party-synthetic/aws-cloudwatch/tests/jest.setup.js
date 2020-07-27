// Patch tests to expose name
jasmine.getEnv().addReporter({
    specStarted: result => global._testName = `${result.id}-${result.description}`, // fullName includes all describes as well
});
