// __mocks__/axios.js - Mock axios for testing
export default {
  create: jest.fn(() => ({
    get: jest.fn(() => Promise.resolve({ data: {} })),
    post: jest.fn(() => Promise.resolve({ data: {} })),
    put: jest.fn(() => Promise.resolve({ data: {} })),
    delete: jest.fn(() => Promise.resolve({ data: {} })),
    patch: jest.fn(() => Promise.resolve({ data: {} })),
    interceptors: {
      request: {
        use: jest.fn(),
        handlers: [{
          fulfilled: jest.fn((config) => config),
          rejected: jest.fn((error) => Promise.reject(error))
        }]
      },
      response: {
        use: jest.fn(),
        handlers: [{
          fulfilled: jest.fn((response) => response),
          rejected: jest.fn((error) => Promise.reject(error))
        }]
      }
    }
  })),
  get: jest.fn(() => Promise.resolve({ data: {} })),
  post: jest.fn(() => Promise.resolve({ data: {} })),
  put: jest.fn(() => Promise.resolve({ data: {} })),
  delete: jest.fn(() => Promise.resolve({ data: {} })),
  patch: jest.fn(() => Promise.resolve({ data: {} })),
};