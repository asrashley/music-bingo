import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';
import { useForm } from "react-hook-form";

import { Input } from '../../components';
import { ModalDialog } from '../../components';

import { createGuestAccount, loginUser } from '../userSlice';
import routes from '../../routes';
import { loginUsernameRules, passwordRules } from '../rules';
import '../styles/user.scss';

function LoginDialogForm(props) {
  const { alert, onCancel, user, playAsGuest } = props;
  let { className } = props;
  const { register, handleSubmit, formState, errors, getValues, setError } = useForm({
    mode: 'onChange',
    defaultValues: {
      username: user.username || user.guest.username,
      password: user.password || user.guest.password,
    }
  });

  function submitWrapper(data) {
    const { onSubmit } = props;
    onSubmit(data).then(result => {
      if (result !== true && result !== undefined) {
        setError(result);
      }
    });
  };

  if (user.isFetching === true) {
    className += ' submitting';
  }
  const showCreateGuest = (playAsGuest && user.guest.valid &&
                           !(user.guest.username && user.guest.password));
  const footer = (
    <React.Fragment>
      <div className="row border-bottom">
        <span className="col">
          <Link className="btn btn-primary register-button"
                disabled={user.isFetching}
            to={reverse(`${routes.register}`)}>Create an account</Link></span>
        <p className="password-reset col" >
          <Link to={reverse(`${routes.passwordReset}`)}>Help, I have forgotten my password!</Link>
        </p>
      </div>
      <div className="row">
        <span className="col">
          {showCreateGuest && <button onClick={playAsGuest}
                                      className="btn btn-primary guest-button"
                                      disabled={user.isFetching}>Play as a guest</button>}
          <button type="submit" className="btn btn-success btn-lg login-button"
            disabled={user.isFetching}>Login</button>
        </span>
      </div>
    </React.Fragment>
  );
  return (
    <form onSubmit={handleSubmit(submitWrapper)} className={className}>
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
        <div className="form-check">
          <input className="form-check-input" type="checkbox" name="rememberme"
                 id="rememberMe" ref={register} />
          <label className="form-check-label" htmlFor="rememberMe">
            Remember me
          </label>
        </div>
      </ModalDialog>
    </form>
  );
}

LoginDialogForm.propTypes = {
  alert: PropTypes.string,
  user: PropTypes.object.isRequired,
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
};


class LoginDialog extends React.Component {
  static propTypes = {
    user: PropTypes.object.isRequired,
    dispatch: PropTypes.func.isRequired,
    onCancel: PropTypes.func.isRequired,
    onSuccess: PropTypes.func.isRequired,
    backdrop: PropTypes.bool,
  };

  state = {
    alert: null,
    lastUpdated: 0,
  };

  handleSubmit = ({ password, username, rememberme }) => {
    const { dispatch } = this.props;
    return dispatch(loginUser({ password, username, rememberme }))
      .then(this.submitResponse);
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

  failedLogin = (err) => {
    const lastUpdated = Date.now();
    if (typeof(err) === "object" && err.error) {
      const { error, status } = err;
      if (status !== undefined && status >= 500) {
        this.setState({
          alert: "There is a problem with the server. Please try again later",
          lastUpdated,
        });
      } else {
        this.setState({ alert: error, lastUpdated });
      }
    } else {
      this.setState({
        alert: "Username or password is incorrect",
        lastUpdated,
      });
    }
  };

  playAsGuest = () => {
    const { dispatch, user } = this.props;
    dispatch(createGuestAccount(user.guest.token));
  }

  render() {
    const { backdrop, user, onCancel } = this.props;
    let { alert, lastUpdated } = this.state;
    let className = "login-form";
    if (user.isisFetching === true) {
      className += " loading";
    }
    if (!alert && user.error && lastUpdated < user.lastUpdated) {
      alert = user.error;
    }
    return (
      <div >
        <LoginDialogForm alert={alert} onSubmit={this.handleSubmit} onCancel={onCancel}
                         className={className} user={user} playAsGuest={this.playAsGuest} />
        {backdrop === true && <div className="modal-backdrop fade show"></div>}
      </div>
    );
  }
};

export { LoginDialog };
