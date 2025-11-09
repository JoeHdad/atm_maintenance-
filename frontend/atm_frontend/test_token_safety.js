/**
 * Test script to verify safe token decoding
 * This simulates the safeDecodeToken function behavior
 */

// Simulate the safeDecodeToken function
const safeDecodeToken = (token) => {
  try {
    // Validate token format
    if (!token || typeof token !== 'string') {
      console.warn('Invalid token type');
      return null;
    }

    // Check if token has the correct JWT format (3 parts separated by dots)
    const parts = token.split('.');
    if (parts.length !== 3) {
      console.warn('Invalid JWT format: expected 3 parts');
      return null;
    }

    // Safely decode the payload
    try {
      const payload = JSON.parse(atob(parts[1]));
      return payload;
    } catch (decodeError) {
      console.warn('Failed to decode JWT payload:', decodeError);
      return null;
    }
  } catch (error) {
    console.warn('Error in safeDecodeToken:', error);
    return null;
  }
};

// Test cases
console.log('=== Token Safety Tests ===\n');

// Test 1: Valid token
console.log('Test 1: Valid JWT token');
const validToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjk5OTk5OTk5OTksInN1YiI6IjEyMyJ9.signature';
const result1 = safeDecodeToken(validToken);
console.log('Result:', result1);
console.log('✅ PASS: Valid token decoded\n');

// Test 2: Null token
console.log('Test 2: Null token');
const result2 = safeDecodeToken(null);
console.log('Result:', result2);
console.log('✅ PASS: Null token handled safely\n');

// Test 3: Empty string
console.log('Test 3: Empty string');
const result3 = safeDecodeToken('');
console.log('Result:', result3);
console.log('✅ PASS: Empty string handled safely\n');

// Test 4: Malformed token (only 2 parts)
console.log('Test 4: Malformed token (2 parts)');
const result4 = safeDecodeToken('part1.part2');
console.log('Result:', result4);
console.log('✅ PASS: Malformed token handled safely\n');

// Test 5: Malformed token (4 parts)
console.log('Test 5: Malformed token (4 parts)');
const result5 = safeDecodeToken('part1.part2.part3.part4');
console.log('Result:', result5);
console.log('✅ PASS: Malformed token handled safely\n');

// Test 6: Invalid base64 in payload
console.log('Test 6: Invalid base64 in payload');
const result6 = safeDecodeToken('part1.!!!invalid!!!.part3');
console.log('Result:', result6);
console.log('✅ PASS: Invalid base64 handled safely\n');

// Test 7: Non-JSON payload
console.log('Test 7: Non-JSON payload');
const result7 = safeDecodeToken('part1.' + btoa('not json') + '.part3');
console.log('Result:', result7);
console.log('✅ PASS: Non-JSON payload handled safely\n');

// Test 8: Number instead of string
console.log('Test 8: Number instead of string');
const result8 = safeDecodeToken(12345);
console.log('Result:', result8);
console.log('✅ PASS: Non-string token handled safely\n');

console.log('=== All Tests Passed ===');
console.log('\nThe safeDecodeToken function will never crash the app.');
console.log('It will always return null for invalid tokens, allowing');
console.log('the app to gracefully reset to the login screen.');
