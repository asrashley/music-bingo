import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';

import { LoginDialog } from './LoginDialog';

/* actions */
import { fetchUserIfNeeded } from '../../user/userSlice';

/* selectors */
import { getUser } from '../../user/userSelectors';

/* data */
import routes from '../../routes';
import { initialState } from '../../app/initialState';

import '../styles/user.scss';

class LoginPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    history: PropTypes.object.isRequired,
    user: PropTypes.object.isRequired,
  };

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(fetchUserIfNeeded());
  }

  componentDidUpdate(prevProps, prevState) {
    const { user } = this.props;
    if (prevProps.user.loggedIn !== user.loggedIn && user.loggedIn === true) {
      this.changePage();
    }
  }

  changePage = () => {
    const { history } = this.props;
    history.push(reverse(`${routes.index}`));
  }

  render() {
    const { user } = this.props;
    const showWelcome = !user.isFetching && user.loggedIn;
    return (
      <div className={!user.loggedIn ? 'modal-open' : ''} id="login-page">
        {!user.loggedIn && <LoginDialog dispatch={this.props.dispatch} onSuccess={this.changePage} user={user} />}
        {showWelcome && <p>
          Welcome {user.username}. You can now go to the < Link to={reverse(`${routes.index}`)}>home page</Link> and start playing!</p>}
      </div>
    );
  }
}

const mapStateToProps = (state, props) => {
  state = state || initialState;
  return {
    user: getUser(state, props),
  };
};

LoginPage = connect(mapStateToProps)(LoginPage);

export { LoginPage };
