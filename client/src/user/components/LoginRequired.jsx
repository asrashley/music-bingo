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

/* types */
import { UserPropType } from '../types/User';

import '../styles/user.scss';

class LoginRequired extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    history: PropTypes.object.isRequired,
    user: UserPropType.isRequired,
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
    const { dispatch, user } = this.props;
    if (user.loggedIn) {
      return null;
    }
    return (
      <LoginDialog
        dispatch={dispatch}
        onSuccess={() => true}
        onCancel={this.changePage}
        user={user}
        backdrop
        />
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
