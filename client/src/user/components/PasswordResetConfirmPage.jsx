import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';
import { push } from '@lagunovsky/redux-react-router';
import { createSelector } from 'reselect';
import { getRouteParams } from '../../routes/routesSelectors';

import { PasswordChangeForm } from './PasswordChangeForm';

import { passwordResetUser } from '../userSlice';
import { routes } from '../../routes/routes';

import '../styles/user.scss';

export class PasswordResetConfirmPageComponent extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func,
    token: PropTypes.string.isRequired
  };

  state = {
    resetSent: false,
  };

  onSubmit = (values) => {
    const { dispatch } = this.props;
    return dispatch(passwordResetUser(values))
      .then((response) => {
        //console.dir(response);
        if (!response) {
          return {
            type: "validate",
            message: "Unknown error",
            name: "email",
          };
        }
        const { payload } = response;
        if (payload.success === true) {
          dispatch(push(reverse(`${routes.index}`)));
          return true;
        }
        return {
          type: "validate",
          message: payload.error,
          name: "email",
        }
      })
      .catch(err => {
        //console.dir(err);
        const error = (err ? `${err}` : 'Unknown error');
        return {
          type: "validate",
          message: error,
          name: "email",
        };
      });
  };

  onCancel = (ev) => {
    const { dispatch } = this.props;
    ev.preventDefault();
    dispatch(push(reverse(`${routes.login}`)));
    return false;
  };

  render() {
    const { token } = this.props;
    return (
      <div className="reset-sent">
        <PasswordChangeForm onSubmit={this.onSubmit}
          onCancel={this.onCancel} token={token} passwordReset />
      </div>
    );
  }
}

const getToken = createSelector([getRouteParams], params => params.token);

const mapStateToProps = (state, ownProps) => {
  return {
    token: getToken(state, ownProps),
  };
};

export const PasswordResetConfirmPage = connect(mapStateToProps)(PasswordResetConfirmPageComponent);
