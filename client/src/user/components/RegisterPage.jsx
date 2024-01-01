import React from 'react';
import PropTypes from 'prop-types';
import { reverse } from 'named-urls';
import { push } from '@lagunovsky/redux-react-router';

import { RegisterForm } from './RegisterForm';
import { checkUser, registerUser } from '../userSlice';
import { routes } from '../../routes/routes';

import '../styles/user.scss';

export class RegisterPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func,
  };

  handleSubmit = ({ email, password, username }) => {
    const { dispatch } = this.props;
    return dispatch(registerUser({ email, password, username })).then(this.submitResponse);
  };

  submitResponse = (result) => {
    const { dispatch } = this.props;
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
      dispatch(push(reverse(`${routes.index}`)));
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
    return (errs);
  };

  onCancel = () => {
    const { dispatch } = this.props;
    dispatch(push(reverse(`${routes.login}`)));
  };

  checkUser = ({ email, username }) => {
    const { dispatch } = this.props;
    return dispatch(checkUser({ email, username }))
      .then((result) => {
        if (!result) {
          return ({ error: 'Unknown error' });
        }
        return result.payload;
      });
  }

  render() {
    return (
      <RegisterForm {...this.props} onSubmit={this.handleSubmit} onCancel={this.onCancel}
        checkUser={this.checkUser}
      />
    );
  }
}
