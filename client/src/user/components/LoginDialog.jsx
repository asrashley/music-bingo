import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';
import { reduxForm, Field, SubmissionError } from 'redux-form';

import { Input } from '../../components';
import { loginUser } from '../userSlice';
import { validateLoginForm } from '../rules';
import { ModalDialog } from '../../components';
import routes from '../../routes';

import '../styles/user.scss';

class LoginDialogForm extends React.Component {
  static propTypes = {
    alert: PropTypes.string,
    handleSubmit: PropTypes.func.isRequired,
    submitting: PropTypes.bool,
    pristine: PropTypes.bool,
    valid: PropTypes.bool,
  };

  render() {
    const { alert, handleSubmit, submitting, pristine, valid, onCancel } = this.props;
    const footer = (
      <div>
        <div className="clearfix">
          <Link className="btn btn-primary register-button"
            to={reverse(`${routes.register}`)}>Create an account</Link>
          <input type="submit" className="btn btn-success login-button" onClick={handleSubmit}
            disabled={pristine || submitting || !valid} value="Login" />
        </div>
        <p className="password-reset" >
          <Link to={reverse(`${routes.passwordReset}`)}>Help, I have forgotten my password!</Link>
        </p>
      </div>
    );
    return (
      <ModalDialog id="login"
        title="Log into Musical Bingo"
        footer={footer} onCancel={onCancel}>
        <form onSubmit={handleSubmit} className={`${pristine ? '' : 'off-was-validated'}`}>
          {alert && <div className="alert alert-warning" role="alert"><span className="error-message">{alert}</span></div>}
          <Field type="text" className="username"
            component={Input}
            label="User name or email address"
            hint="This is the name you used when you registered your account"
            name="username" required />
          <Field type="password" className="password"
            component={Input}
            label="Password"
            name="password"
            required />
        </form>
      </ModalDialog>
    );
  }
}

LoginDialogForm = reduxForm({
  form: 'login',
  validate: validateLoginForm,
})(LoginDialogForm);


class LoginDialog extends React.Component {

  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    onSuccess: PropTypes.func.isRequired,
    backdrop: PropTypes.bool,
  };
  state = {
    alert: null,
  };

  handleSubmit = ({ password, username }) => {
    const { dispatch } = this.props;
    dispatch(loginUser({ password, username }))
      .then(this.submitResponse)
      .catch(this.failedLogin);
  };

  submitResponse = (result) => {
    const { onSuccess } = this.props;
    const { success, error } = result;
    if (success === true) {
      return onSuccess();
    }
    if (error === undefined) {
      throw new SubmissionError({ "_error": 'Unknown error' });
    } else {
      throw new SubmissionError({ "_error": error });
    }
  };

  failedLogin = () => {
    //throw new SubmissionError({"_error":  });
    this.setState({ alert: "Username or password is incorrect" });
  };

  onCancel = (event) => {
    this.setState({ alert: 'You need to login to use this application' });
  };

  render() {
    const { backdrop } = this.props;
    const { alert } = this.state;
    return (
      <div >
        <LoginDialogForm alert={alert} onSubmit={this.handleSubmit} onCancel={this.onCancel} className="register-form" />
        {backdrop === true && <div className="modal-backdrop fade show"></div>}
      </div>
    );
  }
};

export { LoginDialog };
