import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';

import { PasswordChangeForm } from './PasswordChangeForm';

/* actions */
import { fetchUserIfNeeded, changeUserPassword } from '../../user/userSlice';
import { addMessage } from '../../messages/messagesSlice';

/* selectors */
import { getUser } from '../../user/userSelectors';

/* data */
import routes from '../../routes';

import '../styles/user.scss';

class ChangeUserPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    history: PropTypes.object.isRequired,
    user: PropTypes.object.isRequired,
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
    return dispatch(changeUserPassword(values))
      .then((response) => {
        console.dir(response);
        if (!response) {
          return {
            type: "validate",
            message: "Unknown error",
            name: "email",
          };
        }
        const { payload } = response;
        if (payload.success === true) {
          dispatch(addMessage({
            type: "success",
            text: 'Password successfully updated'
          }));
          history.push(reverse(`${routes.user}`));
          return true;
        }
        this.setState({ error: payload.error });
        return {
          type: "validate",
          message: payload.error,
          name: "email",
        };
      })
      .catch(err => {
        console.dir(err);
        const error = (err ? `${err}` : 'Unknown error');
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

ChangeUserPage = connect(mapStateToProps)(ChangeUserPage);

export { ChangeUserPage };
