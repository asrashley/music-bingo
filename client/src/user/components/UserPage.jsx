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

class UserPage extends React.Component {
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
    return (
      <div id="user-page">
        <p>
          Hello {user.username}.
          </p>
        <div className="user-commands">
          <Link to={reverse(`${routes.changeUser}`)} className="btn btn-lg btn-warning change-user mt-3 mb-5">Change password or email address</Link>
          <Link to={reverse(`${routes.logout}`)} className="btn btn-lg btn-primary logout mb-5">Log out</Link>
        </div>
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

UserPage = connect(mapStateToProps)(UserPage);

export { UserPage };
