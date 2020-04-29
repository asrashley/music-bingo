import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';
import { reduxForm, Field, SubmissionError } from 'redux-form';

import { Input } from '../../components';
import { checkUser, registerUser } from '../userSlice';
import { minUsernameLength, minPasswordLength } from '../constants';
import { validateRegistrationForm } from '../rules';
import routes from '../../routes';

import '../styles/user.scss';

class RegisterForm extends React.Component {
  static propTypes = {
    handleSubmit: PropTypes.func.isRequired,
    submitting: PropTypes.bool,
    pristine: PropTypes.bool,
    valid: PropTypes.bool,
  };

  render() {
    const { handleSubmit, submitting, pristine, valid, onCancel } = this.props;
    /* {`register-form ${pristine ? '' : 'off-was-validated'}`} */
    return (
      <form onSubmit={handleSubmit} className="register-form" >
        <Field type="text" className="username"
          component={Input}
          label="User name"
          hint="This is the name you will use to log in and the name that will be visible to other players."
          minLength={minUsernameLength}
          name="username" required />
        <Field name="email" label="Email address"
          component={Input}
          hint="We'll never share your email with anyone else."
          required />
        <Field type="password" className="password"
          component={Input}
          label="Password"
          minLength={minPasswordLength}
          name="password"
          hint={`The password needs to be at least ${minPasswordLength} characters in length.`}
          required />
        <Field type="password" className="password"
          component={Input}
          label="Confirm Password"
          minLength={minPasswordLength}
          name="confirmPassword"
          hint="Please enter the password a second time to make sure you have typed it correctly"
          required />
        <div className="form-text text-muted">* = a required field</div>
        <div className="form-group modal-footer">
        <button type="submit" className="btn btn-primary" disabled={pristine || submitting || !valid}>Register</button>
          <button type="cancel" name="cancel" className="btn btn-danger" onClick={onCancel}>Cancel</button>
          </div>

      </form>
    );
  }
}

const asyncValidate = (values, dispatch) => {
  return dispatch(checkUser(values))
    .then((result) => {
      const { email, username, error } = result;
      if (error) {
        return Promise.reject({ username: error });
      }
      if (username === true) {
        return Promise.reject({ username: "That username is already taken" });
      }
      if (email === true) {
        return Promise.reject({ email: "That email address is already registered" });
      }
    });
};

RegisterForm = reduxForm({
  form: 'register',
  validate: validateRegistrationForm,
  asyncValidate,
  asyncBlurFields: ['username', 'email'],
  asyncChangeFields: ['username']
})(RegisterForm);

class RegisterPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func,
    history: PropTypes.object,
  };


  handleSubmit = ({ email, password, username }) => {
    const { dispatch } = this.props;
    dispatch(registerUser({ email, password, username })).then(this.submitResponse);
  }

  submitResponse = (result) => {
    const { success, error } = result;
    const { history } = this.props;
    if (success === true) {
      history.push(reverse(`${routes.index}`));
    } else {
      const { username, email } = error || {};
      if (username === undefined && email === undefined) {
        throw new SubmissionError({ "_error": error });
      }
      throw new SubmissionError(error);
    }
  }

  onCancel = () => {
    const { history } = this.props;
    history.push(reverse(`${routes.login}`));
  }

  render() {
    return (
      <RegisterForm {...this.props} onSubmit={this.handleSubmit} onCancel={this.onCancel}/>
    );
  }
};

RegisterPage = connect()(RegisterPage);

export {
  RegisterPage
};
