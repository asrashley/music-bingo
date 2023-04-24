import React from 'react';
import PropTypes from 'prop-types';
import log from 'loglevel';

import { createGuestAccount, loginUser } from '../userSlice';
import { LoginDialogForm } from './LoginDialogForm';
import { UserPropType } from '../types/User';

import '../styles/user.scss';

class LoginDialog extends React.Component {
  static propTypes = {
    user: UserPropType.isRequired,
    dispatch: PropTypes.func.isRequired,
    onCancel: PropTypes.func.isRequired,
    onSuccess: PropTypes.func.isRequired,
    backdrop: PropTypes.bool,
  };

  state = {
    alert: null,
    lastUpdated: 0,
  };
  mounted = false;

  componentDidMount() {
    this.mounted = true;
  }

  componentWillUnmount() {
    this.mounted = false;
  }

  handleSubmit = ({ password, username, rememberme }) => {
    const { dispatch } = this.props;
    return dispatch(loginUser({ password, username, rememberme }))
      .then(this.submitResponse);
  };

  submitResponse = (result) => {
    if (!this.mounted) {
      return true;
    }
    const { onSuccess } = this.props;
    const { accessToken, error, status } = result.payload ? result.payload : result;
    if (error === undefined && accessToken !== undefined) {
      onSuccess();
      return true;
    }
    this.failedLogin(status, error);
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

  failedLogin(status, err) {
    const lastUpdated = Date.now();
    log.debug(`login failed ${status} ${err}`);
    if (status !== undefined && status >= 500) {
      this.setState({
        alert: "There is a problem with the server. Please try again later",
        lastUpdated,
      });
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
  };

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
