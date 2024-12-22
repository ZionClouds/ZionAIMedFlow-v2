// filepath: /c:/Users/BalaSubrahmanyam/OneDrive - ZionClouds/Documents/Workspace/ZionAIMedFlow/src/frontends/pdfapprover/jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/__tests__/**/*.[jt]s?(x)', '**/?(*.)+(spec|test).[tj]s?(x)'],
  transform: {
    '^.+\\.(ts|tsx)$': 'babel-jest',
  },
};