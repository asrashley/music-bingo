import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { loginUser } from '../userSlice';
import { ModalDialog } from '../../components';
import routes from '../../routes';
import { minUsernameLength, minPasswordLength } from '../constants';

class LoginDialog extends React.Component {

  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    onSuccess: PropTypes.func.isRequired,
  };

  constructor(props) {
    super(props);
    this.state = {
      username: '',
      password: '',
      error: null,
    };
  }

  handleSubmit = (event) => {
    event.preventDefault();
    const { dispatch } = this.props;
    const { password, username } = this.state;
    const valid = this.isValid();
    if (valid === true) {
      dispatch(loginUser({ password, username }))
        .then(this.afterLogin)
        .catch(this.failedLogin);
    } else {
      this.setState({ error: valid });
    }
  };

  afterLogin = (result) => {
    const { onSuccess } = this.props;
    const { success, error } = result;
    if (success === true) {
      return onSuccess();
    }
    if (error === undefined) {
      this.setState({ error: 'Unknown error' });
    } else {
      this.setState({ error });
    }

  };

  failedLogin = (result) => {
    const { error } = result || {};
    if (error === undefined) {
      this.setState({ error: 'Unknown error' });
    } else {
      this.setState({ error });
    }
  };

  updateUsername = (event) => {
    this.setState({ username: event.target.value });
  };

  updatePassword = (event) => {
    this.setState({ password: event.target.value });
  };

  isValid() {
    const { username, password } = this.state;
    if (username.length >= minUsernameLength && password.length >= minPasswordLength) {
      return true;
    }
    return "Invalid username or password";
  }

  onCancel = (event) => {
    this.setState({ error: 'You need to login to use this application' });
  };

  render() {
    const { error, username, password } = this.state;
    const footer = (
      <p className="register-link">
        Don't have an account?
        <Link className="btn btn-primary register-button"
          to={reverse(`${routes.register}`)}>Register</Link>
      </p>

    );
    return (
      <ModalDialog id="login"
        title="Log into Musical Bingo"
        footer={footer} onCancel={this.onCancel}>
        <form className="login-form" onSubmit={this.handleSubmit}>
          {error && <div className="alert alert-warning" role="alert">
            <p className="error-message">Login failed, the username or password is incorrect</p>
            <p className="error-detail">{error}</p>
          </div>}
          <div className="form-group">
            <label htmlFor="username">User name</label>
            <input type="text" className="form-control"
              value={username} onChange={this.updateUsername}
              id="id_username" name="username" aria-describedby="usernameHelp" />
            <small id="usernameHelp" className="form-text text-muted">
              This is the user name you specified when registering
          </small>
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input type="password" className="form-control"
              value={password} onChange={this.updatePassword}
              id="id_password" name="password" />
          </div>
          <div className="form-group">
            <button type="submit" className="btn btn-success login-button" onClick={this.handleSubmit} > Login</ button>
          </div>

        </form>
      </ModalDialog>
    );
  }
};

export { LoginDialog };
