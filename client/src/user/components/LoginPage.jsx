import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { reverse } from 'named-urls';

import { LoginDialog } from './LoginDialog';
import { loginUser } from '../userSlice';
import routes from '../../routes';
import { initialState } from '../../app/initialState';
import { fetchUserIfNeeded, userIsLoggedIn } from '../../user/userSlice';
import '../styles/user.scss';

class LoginPage extends React.Component {
    componentDidMount() {
        const { dispatch } = this.props;
        dispatch(fetchUserIfNeeded());
    }

    render() {
        return (
            <div className="modal-open" id="login-page">
                <LoginDialog {...this.props} />
            </div>
        );
    }
}

LoginPage.propTypes = {
    dispatch: PropTypes.func,
    history: PropTypes.object,
};

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
