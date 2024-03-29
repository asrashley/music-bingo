import { isAlphanumeric, isEmail } from 'validator';
import { minUsernameLength, minPasswordLength } from './constants';

export const loginUsernameRules = () => ({
  required: true,
  validate: (value) => {
    if (!value) {
      return 'Required';
    }
    if (!isAlphanumeric(value, 'en-GB', { ignore: '-.' }) && !isEmail(value)) {
      return 'Username or email address required';
    }
    return true;
  }
});

export const usernameRules = (getValues, action) => ({
  required: true,
  validate: (value) => {
    return new Promise(resolve => {
      if (value.length < minUsernameLength) {
        return resolve(`Username must be at least ${minUsernameLength} characters`);
      }
      if (!isAlphanumeric(value, 'en-GB', { ignore: '-.' })) {
        return resolve('No spaces or special characters are allowed in a username');
      }
      if (action === undefined) {
        return resolve(true);
      }
      return resolve(action({ username: value })
        .then((result) => {
          const { username, error } = result;
          if (error) {
            return error;
          }
          if (username === true) {
            return "That username is already taken";
          }
          return true;
        }));
    });
  }
});

export const emailRules = (getValues, action) => ({
  required: true,
  validate: (value) => new Promise(resolve => {
    if (!isEmail(value)) {
      return resolve('Invalid email address');
    }
    if (action === undefined) {
      return resolve(true);
    }
    return resolve(action({ email: value })
      .then((result) => {
        const { email, error } = result;
        if (error) {
          return error;
        }
        if (email === true) {
          return "That email address is already registered";
        }
        return true;
      }));
  })
});

export const passwordRules = () => ({
  required: 'A password is required',
  validate: {
    minLength: (value) => value.length >= minPasswordLength || `Password must be at least ${minPasswordLength} characters`
  }
});

export const passwordConfirmRules = (getValues) => ({
  required: 'Please confirm password',
  validate: {
    minLength: (value) => value.length >= minPasswordLength || `Password must be at least ${minPasswordLength} characters`,
    matchesPreviousPassword: (value) => {
      const { password } = getValues();
      return password === value || 'Does not match password';
    },
  }
});

export const validatePasswordResetForm = values => {
  const errors = {};
  if (!values.email) {
    errors.email = 'Required';
  } else if (!isEmail(values.email)) {
    errors.email = 'Invalid email address';
  }
  return errors;
};
