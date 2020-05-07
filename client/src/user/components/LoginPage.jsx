import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';

import { LoginDialog } from './LoginDialog';
import { LogoutDialog } from './LogoutDialog';
import routes from '../../routes';
import { initialState } from '../../app/initialState';
import { fetchUserIfNeeded, userIsLoggedIn, logoutUser } from '../../user/userSlice';
import '../styles/user.scss';

class LoginPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    history: PropTypes.object.isRequired,
    user: PropTypes.object.isRequired,
  };

  state = {
    user: {
      pk: -1,
      username: '',
    }
  };

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(fetchUserIfNeeded());
  }

  changePage = () => {
    const { history } = this.props;
    history.push(reverse(`${routes.index}`));
  }

  logoutUser = () => {
    const { dispatch } = this.props;
    dispatch(logoutUser());
  }
  
  render() {
    const { isFetching, loggedIn } = this.props;
    const showLogin = !isFetching && !loggedIn;
    return (
      <div className={showLogin ? 'modal-open' : ''} id="login-page">
        {showLogin && <LoginDialog dispatch={this.props.dispatch} onSuccess={this.changePage} />}
        {loggedIn && <LogoutDialog dispatch={this.props.dispatch} onCancel={this.changePage} onConfirm={this.logoutUser} />}
      </div>
    );
  }
}

const mapStateToProps = (state) => {
  state = state || initialState;
  const { user, router } = state;
  const { location } = router;
  return {
    loggedIn: userIsLoggedIn(state),
    isFetching: user.isFetching,
    user,
    location,
  };
};

LoginPage = connect(mapStateToProps)(LoginPage);

export { LoginPage };
