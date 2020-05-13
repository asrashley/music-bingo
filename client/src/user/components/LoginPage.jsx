import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';

import { LoginDialog } from './LoginDialog';
import routes from '../../routes';
import { initialState } from '../../app/initialState';
import { fetchUserIfNeeded, userIsLoggedIn } from '../../user/userSlice';
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

  componentDidUpdate(prevProps, prevState) {
    const { loggedIn } = this.props;
    if (prevProps.loggedIn !== loggedIn && loggedIn === true) {
      this.changePage();
    }
  }

  changePage = () => {
    const { history } = this.props;
    history.push(reverse(`${routes.index}`));
  }

  render() {
    const { isFetching, loggedIn, user } = this.props;
    const showLogin = !isFetching && !loggedIn;
    return (
      <div className={showLogin ? 'modal-open' : ''} id="login-page">
        {showLogin && <LoginDialog dispatch={this.props.dispatch} onSuccess={this.changePage} user={user} />}
        {!showLogin && <p>
          Welcome {user.username}. You can now go to the < Link to={reverse(`${routes.index}`)}>home page</Link> and start playing!</p>}
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
