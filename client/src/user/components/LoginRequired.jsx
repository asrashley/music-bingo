import React, { useEffect } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';
import { push } from '@lagunovsky/redux-react-router';

import { LoginDialog } from './LoginDialog';

/* actions */
import { fetchUserIfNeeded } from '../../user/userSlice';

/* selectors */
import { getUser } from '../../user/userSelectors';

/* data */
import { routes } from '../../routes/routes';

/* types */
import { UserPropType } from '../types/User';

import '../styles/user.scss';

function LoginRequiredComponent({ children, dispatch, user }) {
  useEffect(() => {
    dispatch(fetchUserIfNeeded());
  }, [dispatch]);

  const changePage = () => {
    dispatch(push(reverse(`${routes.index}`)));
  }

  if (user.loggedIn) {
    return <React.Fragment>{children}</React.Fragment>;
  }
  return (
    <LoginDialog
      dispatch={dispatch}
      onSuccess={() => true}
      onCancel={changePage}
      user={user}
      backdrop
    />
  );
}

LoginRequiredComponent.propTypes = {
  children: PropTypes.node,
  dispatch: PropTypes.func.isRequired,
  user: UserPropType.isRequired,
};


const mapStateToProps = (state, props) => {
  return {
    user: getUser(state, props),
  };
};

export const LoginRequired = connect(mapStateToProps)(LoginRequiredComponent);
