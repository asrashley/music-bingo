import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';
import log from 'loglevel';
import { push } from '@lagunovsky/redux-react-router';

import { PasswordChangeForm } from './PasswordChangeForm';

/* actions */
import { fetchUserIfNeeded, changeUserPassword } from '../../user/userSlice';
import { addMessage } from '../../messages/messagesSlice';

/* selectors */
import { getUser } from '../../user/userSelectors';

/* data */
import { routes } from '../../routes/routes';
import { UserPropType } from '../types/User';

import '../styles/user.scss';

export class ChangeUserPageComponent extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    user: UserPropType.isRequired,
  };

  state = {
    error: '',
  };

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(fetchUserIfNeeded());
  }

  onSubmit = async (values) => {
    const { dispatch } = this.props;
    log.debug('change user');
    const { payload } = await dispatch(changeUserPassword(values));
    if (payload?.success === true) {
      log.debug('change password successful');
      dispatch(addMessage({
        type: "success",
        text: 'Password successfully updated'
      }));
      dispatch(push(reverse(`${routes.user}`)));
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
  };

  onCancel = (ev) => {
    const { dispatch } = this.props;
    ev.preventDefault();
    dispatch(push(reverse(`${routes.user}`)));
    return false;
  };

  render() {
    const { user } = this.props;
    const { error } = this.state;
    return (
      <div id="change-user-page">
        <PasswordChangeForm alert={error} onSubmit={this.onSubmit} key={user.pk}
          onCancel={this.onCancel} token="" user={user} />
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
