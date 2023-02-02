import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';

import { LoginDialog } from './LoginDialog';

/* actions */
import { fetchUserIfNeeded } from '../../user/userSlice';

/* selectors */
import { getUser } from '../../user/userSelectors';

/* data */
import routes from '../../routes';

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

  changePage = () => {
    const { history } = this.props;
    history.push(reverse(`${routes.index}`));
  }

  render() {
    const { user } = this.props;
    if (user.loggedIn) {
      return <React.Fragment/>;
    }
    return (
      <LoginDialog dispatch={this.props.dispatch} onSuccess={() => true}
                   onCancel={this.changePage} backdrop user={user} />
    );
  }
}

const mapStateToProps = (state, props) => {
  return {
    user: getUser(state, props),
  };
};

LoginRequired = connect(mapStateToProps)(LoginRequired);

export { LoginRequired };
