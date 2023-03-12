import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';

import { PasswordChangeForm } from './PasswordChangeForm';

import { passwordResetUser } from '../userSlice';
import routes from '../../routes';
import { HistoryPropType } from '../../types/History';

import '../styles/user.scss';

export class PasswordResetConfirmPageComponent extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func,
    history: HistoryPropType.isRequired,
    token: PropTypes.string.isRequired
  };

  state = {
    resetSent: false,
    alert: '',
  };

  onSubmit = (values) => {
    const { history, dispatch } = this.props;
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
          history.push(reverse(`${routes.index}`));
          return true;
        }
        this.setState({ alert: payload.error });
        return {
          type: "validate",
          message: payload.error,
          name: "email",
        }
      })
      .catch(err => {
        //console.dir(err);
        const error = (err ? `${err}` : 'Unknown error');
        this.setState({ alert: error });
        return {
          type: "validate",
          message: error,
          name: "email",
        };
      });
  };

  onCancel = (ev) => {
    const { history } = this.props;
    ev.preventDefault();
    history.push(reverse(`${routes.login}`));
    return false;
  };

  render() {
    const { alert } = this.state;
    const { token } = this.props;
    return (
      <div className="reset-sent">
        <PasswordChangeForm alert={alert} onSubmit={this.onSubmit}
          onCancel={this.onCancel} token={token} passwordReset />
      </div>
    );
  }
};

const mapStateToProps = (state, ownProps) => {
  const { token } = ownProps.match.params;
  return {
    token
  }
}

export const PasswordResetConfirmPage = connect(mapStateToProps)(PasswordResetConfirmPageComponent);
