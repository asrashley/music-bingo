import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { logoutUser } from '../userSlice';
import routes from '../../routes';

import '../styles/user.scss';

import { UserPropType } from '../types/User';

/* This component is a big unusual as it doesn't directly use the data from the
 * Redux store. It copies the current user into its own state and then logs out
 * the user. The copy of the user in the state is used in the render() function,
 * so that it can display the name of the user has logged out
 */
class LogoutPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    user: UserPropType.isRequired,
  };

  constructor(props) {
    super(props);
    this.state = {
      user: null,
    };
  }
  componentDidMount() {
    const { dispatch } = this.props;
    this.setState((state, props) => {
      const { user } = props;
      return { user };
    }, () => dispatch(logoutUser()));
  }

  render() {
    const { user } = this.state;
    return (
      <form onSubmit={this.handleSubmit} className="logout-form">
        <div className="form-group">
          {user !== null && <h2>Goodbye {user.username}</h2>}
          <p>Thank you for using this site</p>
        </div>
        <Link to={reverse(`${routes.login}`)} className="btn btn-primary">Log in again</Link>
      </form>
    );
  }
}


const mapStateToProps = (state) => {
  const { user } = state;
  return {
    user,
  };
};

LogoutPage = connect(mapStateToProps)(LogoutPage);

export { LogoutPage };
