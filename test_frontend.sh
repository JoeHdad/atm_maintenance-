#!/bin/bash

# Test script for ATM Maintenance System Frontend

echo "🚀 Starting Frontend Tests..."

# Navigate to frontend directory
cd "$(dirname "$0")/frontend/atm_frontend" || exit 1

# Function to run tests with error handling
run_tests() {
  echo "\n🔍 Running $1 tests..."
  if [ "$1" == "integration" ]; then
    npm test -- --testPathPattern="__tests__/TechnicianForm.test.js" --watchAll=false
  elif [ "$1" == "e2e" ]; then
    npx cypress run --spec "cypress/e2e/technician.cy.js"
  fi
  
  if [ $? -ne 0 ]; then
    echo "❌ $1 tests failed!"
    exit 1
  fi
  echo "✅ $1 tests passed!"
}

# Run integration tests
run_tests "integration"

# Run E2E tests if Cypress is installed
if [ -d "node_modules/cypress" ]; then
  run_tests "e2e"
else
  echo "\n⚠️  Cypress not found. Skipping E2E tests."
  echo "   Run 'npm install --save-dev cypress @testing-library/cypress msw' to install Cypress."
fi

echo "\n✨ All tests completed successfully!"
