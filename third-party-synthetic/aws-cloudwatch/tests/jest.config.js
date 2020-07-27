// For a detailed explanation regarding each configuration property, visit:
// https://jestjs.io/docs/en/configuration.html

module.exports = {
  clearMocks: true,
  coverageDirectory: "coverage",
  rootDir: "./",
  setupFilesAfterEnv: ['./jest.setup.js'],
  testEnvironment: "node",
  testMatch: [
     "**/*.spec.ts",
  ],
  testPathIgnorePatterns: [
    "\\\\node_modules\\\\",
    "\\\\temp\\\\",
  ],
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
  },
};
