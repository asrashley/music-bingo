import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';
import log from 'loglevel';

import { RegisterForm } from './RegisterForm';
import { checkUser, registerUser } from '../userSlice';
import routes from '../../routes';

import '../styles/user.scss';

class RegisterPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func,
    history: PropTypes.object,
  };


  handleSubmit = ({ email, password, username }) => {
    const { dispatch } = this.props;
    return dispatch(registerUser({ email, password, username })).then(this.submitResponse);
  };

  submitResponse = (result) => {
    const { history } = this.props;
    if (!result || !result.payload) {
      return [{
        type: "validate",
        message: 'Unknown error',
        name: 'email',
      }];
    }
    const { payload } = result;
    const { success, error } = payload;
    if (success === true) {
      history.push(reverse(`${routes.index}`));
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
    return(errs);
  };

  onCancel = () => {
    const { history } = this.props;
    log.debug('Registration cancelled');
    history.push(reverse(`${routes.login}`));
  };

  checkUser = ({ email, username }) => {
    const { dispatch } = this.props;
    return dispatch(checkUser({ email, username }))
      .then((result) => {
        if (!result) {
          return ({ error: 'Unknown error' });
        }
        return result.payload;
      })
      .catch(err => {
        if (typeof (err) === 'object') {
          const { status, statusText } = err;
          if (status === 500) {
            return ({ error: "There is a problem with the server. Please try again later" });
          }
          if (statusText !== undefined) {
            return ({ error: statusText });
          }
          return ({ error: 'Unknown error' });
        }
        return ({ error: `${err}` });
      });
  }

  render() {
    return (
      <RegisterForm {...this.props} onSubmit={this.handleSubmit} onCancel={this.onCancel}
        checkUser={this.checkUser}
      />
    );
  }
};

RegisterPage = connect()(RegisterPage);

export {
  RegisterPage
};
