import React from 'react';
import PropTypes from 'prop-types';
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
    history: PropTypes.func.isRequired,
  };

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(fetchUserIfNeeded());
  }

  onSuccess = () => {
    const { history } = this.props;
    history.push(reverse(`${routes.index}`));
  }

  render() {
    return (
      <div className="modal-open" id="login-page">
        <LoginDialog dispatch={this.props.dispatch} onSuccess={this.onSuccess} />
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  state = state || initialState;
  const { user, router } = state;
  const { location } = router;
  return {
    loggedIn: userIsLoggedIn(state),
    user,
    location,
  };
};

LoginPage = connect(mapStateToProps)(LoginPage);

export { LoginPage };
