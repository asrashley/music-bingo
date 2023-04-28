import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';
import log from 'loglevel';

import { PasswordChangeForm } from './PasswordChangeForm';

/* actions */
import { fetchUserIfNeeded, changeUserPassword } from '../../user/userSlice';
import { addMessage } from '../../messages/messagesSlice';

/* selectors */
import { getUser } from '../../user/userSelectors';

/* data */
import routes from '../../routes';
import { UserPropType } from '../types/User';
import { HistoryPropType } from '../../types/History';

import '../styles/user.scss';

export class ChangeUserPageComponent extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    history: HistoryPropType.isRequired,
    user: UserPropType.isRequired,
  };

  state = {
    error: '',
  };

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(fetchUserIfNeeded());
  }

  onSubmit = (values) => {
    const { history, dispatch } = this.props;
    log.debug('change user');
    return dispatch(changeUserPassword(values))
      .then((response) => {
        const { payload } = response;
        if (payload?.success === true) {
          log.debug('change password successful');
          dispatch(addMessage({
            type: "success",
            text: 'Password successfully updated'
          }));
          history.push(reverse(`${routes.user}`));
          return true;
        }
        const { error = "Unknown error" } = payload;
        log.warn(`failed to change password: "${error}"`);
        this.setState({ error });
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
    history.push(reverse(`${routes.user}`));
    return false;
  };


  render() {
    const { user } = this.props;
    const { error } = this.state;
    return (
      <div id="change-user-page">
        <PasswordChangeForm alert={error} onSubmit={this.onSubmit} key={user.pk}
          onCancel={this.onCancel} token="" user={user}/>
      </div>
    );
  }
}

const mapStateToProps = (state, props) => {
  return {
    user: getUser(state, props),
  };
};

export const ChangeUserPage = connect(mapStateToProps)(ChangeUserPageComponent);
