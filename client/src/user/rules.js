import { isAlphanumeric, isEmail } from 'validator';
import { minUsernameLength, minPasswordLength } from './constants';

export const validateUsername = values => {
  const errors = {};
  if (!values.username) {
    errors.username = 'Required';
  } else if (!isAlphanumeric(values.username)) {
    errors.username = 'No spaces or special characters are allowed in a username';
  } else if (values.username.length < minUsernameLength) {
    errors.username = `Username must be at least ${minUsernameLength} characters`;
  }
  return errors;
}

export const validateRegistrationForm = values => {
  const errors = validateUsername(values);
  if (!values.email) {
    errors.email = 'Required';
  } else if (!isEmail(values.email)) {
    errors.email = 'Invalid email address';
  }
  if (!values.password) {
    errors.password = 'Required';
  } else if (values.password.length < minPasswordLength) {
    errors.password = `Password must be at least ${minPasswordLength} characters`;
  }
  if (!errors.password) {
    if (!values.confirmPassword) {
      errors.confirmPassword = 'Required';
    } else if (values.password !== values.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }
  }
  console.dir(errors);
  return errors;
};
