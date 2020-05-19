import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { LoginDialog } from './LoginDialog';

/* actions */
import { fetchUserIfNeeded } from '../../user/userSlice';

/* selectors */
import { getUser } from '../../user/userSelectors';

/* data */
import { initialState } from '../../app/initialState';

import '../styles/user.scss';

class LoginRequired extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    history: PropTypes.object.isRequired,
    user: PropTypes.object.isRequired,
  };

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(fetchUserIfNeeded());
  }

  render() {
    const { user } = this.props;
    const showLogin = !user.isFetching && !user.loggedIn;
    if (!showLogin) {
      return <React.Fragment/>;
    }
    return (
      <LoginDialog dispatch={this.props.dispatch} onSuccess={() => true} backdrop user={user} />
    );
  }
}

const mapStateToProps = (state, props) => {
  state = state || initialState;
  return {
    user: getUser(state, props),
  };
};

LoginRequired = connect(mapStateToProps)(LoginRequired);

export { LoginRequired };
