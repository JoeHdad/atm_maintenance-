/// <reference types="cypress" />

// Test data
const testTechnician = {
  username: `tech_${Cypress._.random(1000, 9999)}`,
  password: 'SecurePass123!',
  city: 'Riyadh'
};

describe('Technician Management', () => {
  beforeEach(() => {
    // Start from the login page
    cy.visit('/login');
    
    // Mock login as Data Host
    cy.intercept('POST', '**/api/auth/login/', {
      statusCode: 200,
      body: {
        access: 'fake-access-token',
        refresh: 'fake-refresh-token',
        user: {
          id: 1,
          username: 'host',
          role: 'data_host',
          city: 'Riyadh'
        }
      },
    }).as('loginRequest');

    // Mock successful technician creation
    cy.intercept('POST', '**/api/host/technicians/', {
      statusCode: 201,
      body: {
        id: 100,
        username: testTechnician.username,
        role: 'technician',
        city: testTechnician.city,
        created_at: new Date().toISOString()
      }
    }).as('createTechnician');

    // Login as Data Host
    cy.get('input[name="username"]').type('host');
    cy.get('input[name="password"]').type('host123');
    cy.get('button[type="submit"]').click();
    
    // Wait for login to complete
    cy.wait('@loginRequest');
    
    // Navigate to create technician page
    cy.visit('/create-technician');
  });

  it('successfully loads the technician creation form', () => {
    // Verify form elements
    cy.get('h2').should('contain', 'Create Technician Account');
    cy.get('input[name="username"]').should('be.visible');
    cy.get('input[name="password"]').should('be.visible');
    cy.get('input[name="confirmPassword"]').should('be.visible');
    cy.get('select[name="city"]').should('be.visible');
    cy.get('button[type="submit"]').should('be.visible').and('contain', 'Create Technician');
  });

  it('validates required fields', () => {
    // Try to submit empty form
    cy.get('button[type="submit"]').click();
    
    // Check for validation errors
    cy.contains('Username is required').should('be.visible');
    cy.contains('Password is required').should('be.visible');
    cy.contains('Please confirm your password').should('be.visible');
    cy.contains('City is required').should('be.visible');
    
    // Verify no API call was made
    cy.get('@createTechnician.all').should('have.length', 0);
  });

  it('shows password strength indicator', () => {
    // Test weak password
    cy.get('input[name="password"]').type('weak');
    cy.contains('Weak').should('be.visible');
    
    // Test fair password
    cy.get('input[name="password"]').clear().type('Better123');
    cy.contains('Good').should('be.visible');
    
    // Test strong password
    cy.get('input[name="password"]').clear().type('Very$tr0ngP@ss');
    cy.contains('Strong').should('be.visible');
  });

  it('validates username format', () => {
    // Test invalid characters
    cy.get('input[name="username"]').type('test@user');
    cy.contains('Username must contain only letters, numbers, and underscores').should('be.visible');
    
    // Test minimum length
    cy.get('input[name="username"]').clear().type('ab');
    cy.contains('Username must be at least 3 characters').should('be.visible');
    
    // Test valid username
    cy.get('input[name="username"]').clear().type('valid_user123');
    cy.contains('Username must contain only letters, numbers, and underscores').should('not.exist');
    cy.contains('Username must be at least 3 characters').should('not.exist');
  });

  it('validates password match', () => {
    // Enter mismatched passwords
    cy.get('input[name="password"]').type('Password123');
    cy.get('input[name="confirmPassword"]').type('Different456');
    
    // Trigger blur on confirm password
    cy.get('input[name="confirmPassword"]').blur();
    
    // Check for password mismatch error
    cy.contains('Passwords do not match').should('be.visible');
    
    // Make them match
    cy.get('input[name="confirmPassword"]').clear().type('Password123');
    cy.get('input[name="confirmPassword"]').blur();
    
    // Verify error is gone
    cy.contains('Passwords do not match').should('not.exist');
  });

  it('successfully creates a new technician', () => {
    // Fill in the form
    cy.get('input[name="username"]').type(testTechnician.username);
    cy.get('input[name="password"]').type(testTechnician.password);
    cy.get('input[name="confirmPassword"]').type(testTechnician.password);
    cy.get('select[name="city"]').select(testTechnician.city);
    
    // Submit the form
    cy.get('button[type="submit"]').click();
    
    // Verify API call was made with correct data
    cy.wait('@createTechnician').then((interception) => {
      expect(interception.request.body).to.deep.equal({
        username: testTechnician.username,
        password: testTechnician.password,
        city: testTechnician.city
      });
    });
    
    // Verify success message
    cy.contains(`Technician "${testTechnician.username}" created successfully!`).should('be.visible');
    
    // Verify form is reset
    cy.get('input[name="username"]').should('have.value', '');
    cy.get('input[name="password"]').should('have.value', '');
    cy.get('input[name="confirmPassword"]').should('have.value', '');
    cy.get('select[name="city"]').should('have.value', '');
  });

  it('handles API errors gracefully', () => {
    // Mock API error for duplicate username
    cy.intercept('POST', '**/api/host/technicians/', {
      statusCode: 400,
      body: {
        username: ['A user with that username already exists.']
      }
    }).as('createTechnicianError');
    
    // Fill in the form with duplicate username
    cy.get('input[name="username"]').type('existing_tech');
    cy.get('input[name="password"]').type(testTechnician.password);
    cy.get('input[name="confirmPassword"]').type(testTechnician.password);
    cy.get('select[name="city"]').select(testTechnician.city);
    
    // Submit the form
    cy.get('button[type="submit"]').click();
    
    // Verify error message is displayed
    cy.contains('A user with that username already exists').should('be.visible');
    
    // Verify form is not reset
    cy.get('input[name="username"]').should('have.value', 'existing_tech');
  });

  it('is accessible', () => {
    // Check for accessibility issues
    cy.injectAxe();
    cy.checkA11y();
    
    // Check form labels are properly associated
    cy.get('input[name="username"]').should('have.attr', 'id');
    cy.get('label[for]').first().should('have.attr', 'for')
      .then((id) => {
        cy.get(`#${id}`).should('exist');
      });
  });

  it('is responsive on different screen sizes', () => {
    // Test mobile view
    cy.viewport('iphone-6');
    cy.get('form').should('be.visible');
    
    // Test tablet view
    cy.viewport('ipad-2');
    cy.get('form').should('be.visible');
    
    // Test desktop view
    cy.viewport('macbook-15');
    cy.get('form').should('be.visible');
  });
});
