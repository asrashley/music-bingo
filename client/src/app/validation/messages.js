export default {
  general: {
    missing: 'Please provide the required field',
    invalid: 'Provided value is invalid'
  },

  type: {
    email: {
      missing: 'Please provide an e-mail',
      invalid: 'The e-mail you provided is invalid'
    }
  },

  name: {
    userEmail: {
      async: ({ value, reason }) => {
        return `The e-mail "${value}" is invalid. Reason: ${reason}`;
      }
    }
  }
};
