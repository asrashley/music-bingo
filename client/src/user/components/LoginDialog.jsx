import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';
import { useForm } from "react-hook-form";

import { Input } from '../../components';
import { loginUser } from '../userSlice';
import { ModalDialog } from '../../components';
import routes from '../../routes';
import { loginUsernameRules, passwordRules } from '../rules';
import '../styles/user.scss';

function LoginDialogForm(props) {
  const { alert, onCancel } = props;
  const { register, handleSubmit, formState, errors, getValues, setError } = useForm({
    mode: 'onChange',
  });
  const { isSubmitting } = formState;

  function submitWrapper(data) {
    const { onSubmit } = props;
    onSubmit(data).then(result => {
      if (result !== true) {
        setError(result);
      }
    });
  };

  const footer = (
    <React.Fragment>
      <div className="row border-bottom">
        <span className="col">
          <Link className="btn btn-primary register-button"
            to={reverse(`${routes.register}`)}>Create an account</Link></span>
        <p className="password-reset col" >
          <Link to={reverse(`${routes.passwordReset}`)}>Help, I have forgotten my password!</Link>
        </p>
      </div>
      <div className="row">
        <span className="col">
          <button type="submit" className="btn btn-success login-button"
            disabled={isSubmitting}>Login</button>
        </span>
      </div>
    </React.Fragment>
  );
  return (
    <form onSubmit={handleSubmit(submitWrapper)} >
      <ModalDialog id="login"
        title="Log into Musical Bingo"
        footer={footer} onCancel={onCancel}>
        {alert && <div className="alert alert-warning" role="alert"><span className="error-message">{alert}</span></div>}
        <Input type="text" className="username"
          register={register(loginUsernameRules(getValues))}
          label="User name or email address"
          errors={errors}
          formState={formState}
          hint="This is the name you used when you registered your account"
          name="username" required />
        <Input type="password" className="password"
          register={register(passwordRules(getValues))}
          errors={errors}
          formState={formState}
          label="Password"
          name="password"
          required />
      </ModalDialog>
    </form>
  );
}

LoginDialogForm.propTypes = {
  alert: PropTypes.string,
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
};


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
    return dispatch(loginUser({ password, username }))
      .then(this.submitResponse);
    //.catch(this.failedLogin);
  };

  submitResponse = (result) => {
    const { onSuccess } = this.props;
    const { success, error } = result;
    if (success === true) {
      onSuccess();
      return true;
    }
    const errs = [];
    for (let name in error) {
      if (error[name]) {
        errs.push({
          type: "validate",
          message: error[name],
          name,
        });
      }
    }
    if (errs.length === 0) {
      return (error);
    }
    return errs;
  };

  failedLogin = () => {
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