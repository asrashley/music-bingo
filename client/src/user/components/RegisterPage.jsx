import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';

import { checkUsername, registerUser } from '../userSlice';
import { minUsernameLength, minPasswordLength } from '../constants';
import routes from '../../routes';

import '../styles/user.scss';

class RegisterPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      email: '',
      password: '',
      username: '',
      available: null,
      error: null,
    };
    this.timer = null;
  }

  componentWillUnmount() {
    this.clearTimer();
  }

  clearTimer() {
    if (this.timer !== null) {
      window.clearTimeout(this.timer);
      this.timer = null;
    }
  }

  handleSubmit = (event) => {
    const { dispatch } = this.props;
    const { email, password, username } = this.state;
    event.preventDefault();
    const valid = this.areValuesValid();
    if (valid.all) {
      dispatch(registerUser({ email, password, username })).then(this.submitResponse);
    }
  };

  submitResponse = (result) => {
    const { success, error } = result;
    const { history } = this.props;
    if (success === true) {
      history.push(reverse(`${routes.index}`));
    } else {
      this.setState({ error });
    }
  };

  updateEmail = (event) => {
    this.clearTimer();
    this.setState({ email: event.target.value });
  };

  updatePassword = (event) => {
    this.clearTimer();
    this.setState({ password: event.target.value });
  };

  updateUsername = (event) => {
    this.clearTimer();
    this.setState({ username: event.target.value, available: null });
    this.timer = setTimeout(this.checkUsername, 350);
  };

  checkUsername = () => {
    const { dispatch } = this.props;
    const { username } = this.state;
    if (username.length > 3) {
      dispatch(checkUsername(username)).then(this.checkUsernameResponse);
    }
  };

  checkUsernameResponse = (result) => {
    const available = result.found === false &&
      result.username === this.state.username;
    this.setState({ available });
  };

  areValuesValid() {
    const { available, email, password, username } = this.state;
    const valid = {
      username: available === true && username.length >= minUsernameLength,
      email: email.length > 3,
      password: password.length >= minPasswordLength,
    };
    valid.all = valid.username && valid.email && valid.password;
    return valid;
  }

  render() {
    const { available, email, password, username } = this.state;
    const valid = this.areValuesValid();
    const inputClassName = item =>
      "form-control" + (valid[item] ? "" : " is-invalid");
    let error = 'Username must be at least 4 characters';

    if (available === false) {
      error = 'Sorry, that username is already taken';
    }

    return (
      <form onSubmit={this.handleSubmit} className="register-form">
        <div className="form-group">
          <label html-for="email">Email address</label>
          <input type="email" className={inputClassName('email')}
            value={email}
            onChange={this.updateEmail}
            id="id_email" name="email" aria-describedby="emailHelp" required />
          <small id="emailHelp" className="form-text text-muted">
            We'll never share your email with anyone else.
                        </small>
        </div>
        <div className="form-group">
          <label html-for="password">Password</label>
          <input type="password" className={inputClassName('password')}
            value={password}
            onChange={this.updatePassword} minLength={minPasswordLength}
            id="id_password" name="password" aria-describedby="passwordHelp" required />
          <small id="passwordHelp" className="form-text text-muted">
            The password needs to be at least {minPasswordLength} characters in length.
    </small>
        </div>
        <div className="form-group">
          <label html-for="username">User name</label>
          <input type="text" className={inputClassName('username')}
            value={username}
            onChange={this.updateUsername} minLength={minUsernameLength}
            id="id_username" name="username" aria-describedby="usernameHelp" required />
          <small className="invalid-feedback">{error}</small>
          <small id="usernameHelp" className="form-text text-muted">
            This is the name you will use to log in and the name that will be visible
            to other players.
    </small>
        </div>
        <button type="submit" className={"btn btn-primary" + (valid.all ? "" : " disabled")}
          aria-disabled={!valid.all}
          disabled={!valid.all} > Submit</button>
      </form>
    );
  }
}

RegisterPage.propTypes = {
  dispatch: PropTypes.func,
  history: PropTypes.object,
};

RegisterPage = connect()(RegisterPage);


export { RegisterPage };
