import { isAlphanumeric, isEmail } from 'validator';
import { minUsernameLength, minPasswordLength } from './constants';

export const validateLoginForm = values => {
  const errors = {};
  if (!values.username) {
    errors.username = 'Required';
  } else if (!isAlphanumeric(values.username) && !isEmail(values.username)) {
    errors.username = 'Username or email address required';
  }
  if (!values.password) {
    errors.password = 'Required';
  }
  return errors;
}

export const validateRegistrationForm = values => {
  const errors = {};

  if (!values.username) {
    errors.username = 'Required';
  } else if (!isAlphanumeric(values.username)) {
    errors.username = 'No spaces or special characters are allowed in a username';
  } else if (values.username.length < minUsernameLength) {
    errors.username = `Username must be at least ${minUsernameLength} characters`;
  }
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
  return errors;
};

export const validatePasswordResetForm = values => {
  const errors = {};
  if (!values.email) {
    errors.email = 'Required';
  } else if (!isEmail(values.email)) {
    errors.email = 'Invalid email address';
  }
  return errors;
};