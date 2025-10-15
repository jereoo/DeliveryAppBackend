// __mocks__/js-cookie.js - Mock js-cookie for testing
export default {
  get: jest.fn((name) => {
    const cookies = {
      'access_token': 'mock-access-token',
      'refresh_token': 'mock-refresh-token'
    };
    return cookies[name];
  }),
  set: jest.fn(),
  remove: jest.fn(),
};