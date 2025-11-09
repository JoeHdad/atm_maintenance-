// ***********************************************
// This example support/e2e.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************

// Import commands.js using ES2015 syntax:
import './commands';

// Alternatively you can use CommonJS syntax:
// require('./commands')

// Global error handling
Cypress.on('uncaught:exception', (err, runnable) => {
  // returning false here prevents Cypress from failing the test
  console.error('Uncaught exception:', err);
  return false;
});

// Custom command to login as a specific user role
Cypress.Commands.add('loginAs', (role = 'data_host') => {
  const users = {
    data_host: {
      username: 'host',
      password: 'host123',
      role: 'data_host',
      city: 'Riyadh'
    },
    technician: {
      username: 'tech1',
      password: 'tech123',
      role: 'technician',
      city: 'Jeddah'
    }
  };

  const user = users[role] || users.data_host;
  
  // Mock login API response
  cy.intercept('POST', '**/api/auth/login/', {
    statusCode: 200,
    body: {
      access: `fake-jwt-token-${role}`,
      refresh: 'fake-refresh-token',
      user: {
        id: role === 'data_host' ? 1 : 2,
        username: user.username,
        role: user.role,
        city: user.city
      }
    }
  }).as('loginRequest');

  // Visit login page and submit form
  cy.visit('/login');
  cy.get('input[name="username"]').type(user.username);
  cy.get('input[name="password"]').type(user.password);
  cy.get('button[type="submit"]').click();
  
  // Wait for login to complete
  cy.wait('@loginRequest');
  
  // Verify navigation to dashboard
  cy.url().should('include', '/dashboard');
});

// Custom command to mock API responses
Cypress.Commands.add('mockApiResponse', (method, url, statusCode, response, alias) => {
  const methodLower = method.toLowerCase();
  const aliasName = alias || `${methodLower}${url.replace(/[^a-zA-Z0-9]/g, '')}`;
  
  cy.intercept(method, `${Cypress.env('apiUrl')}${url}`, {
    statusCode,
    body: response
  }).as(aliasName);
  
  return `@${aliasName}`;
});

// Custom command to check form validation
Cypress.Commands.add('checkFormValidation', (fields) => {
  cy.get('form').find('button[type="submit"]').click();
  
  fields.forEach(field => {
    if (field.required) {
      cy.contains(`${field.label} is required`).should('be.visible');
    }
    
    if (field.pattern) {
      // Test invalid pattern
      cy.get(`input[name="${field.name}"]`).type(field.invalidValue || '@invalid');
      cy.contains(field.patternError).should('be.visible');
      
      // Clear and test valid pattern
      cy.get(`input[name="${field.name}"]`).clear().type(field.validValue || 'valid123');
      cy.contains(field.patternError).should('not.exist');
    }
  });
});

// Custom command to fill and submit technician form
Cypress.Commands.add('fillAndSubmitTechnicianForm', (technician) => {
  const { username, password, city } = technician;
  
  cy.get('input[name="username"]').type(username);
  cy.get('input[name="password"]').type(password);
  cy.get('input[name="confirmPassword"]').type(password);
  cy.get('select[name="city"]').select(city);
  
  cy.get('button[type="submit"]').click();
});
