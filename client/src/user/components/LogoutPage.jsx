import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { logoutUser } from '../userSlice';
import routes from '../../routes';
import { initialState } from '../../app/initialState';
import '../styles/user.scss';

class LogoutPage extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func,
    user: PropTypes.object,
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
          {user && <h2>Goodbye {user.username}</h2>}
          <p>Thank you for using this site</p>
        </div>
        <Link to={reverse(`${routes.login}`)} className="btn btn-primary">Log in again</Link>
      </form>
    );
  }
}


const mapStateToProps = (state) => {
  state = state || initialState;
  const { user } = state;
  return {
    user,
  };
};

LogoutPage = connect(mapStateToProps)(LogoutPage);

export { LogoutPage };
