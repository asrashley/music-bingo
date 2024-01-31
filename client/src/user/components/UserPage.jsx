import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { reverse } from 'named-urls';

import { AdminActions } from '../../admin/components/AdminActions';
import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchSettingsIfNeeded } from '../../settings/settingsSlice';

import { getUser } from '../../user/userSelectors';

import { routes } from '../../routes/routes';

import '../styles/user.scss';

export function UserPage() {
  const dispatch = useDispatch();
  const user = useSelector(getUser);

  useEffect(() => {
    dispatch(fetchUserIfNeeded());
  }, [dispatch]);

  useEffect(() => {
    if (user.loggedIn) {
      dispatch(fetchSettingsIfNeeded());
    }
  }, [dispatch, user.loggedIn]);

  return (
    <div id="user-page">
      <div className="user-details border border-secondary rounded">
        <div className="form-group row">
          <label htmlFor="username" className="col-sm-2 col-form-label field">Username</label>
          <div className="col-sm-10">
            <div className="form-control-plaintext value" id="username">
              {user.username}
            </div>
          </div>
        </div>
        <div className="form-group row">
          <label htmlFor="email" className="col-sm-2 col-form-label">Email</label>
          <div className="col-sm-10">
            <div className="form-control-plaintext" id="email">
              {user.email}
            </div>
          </div>
        </div>
      </div>
      <div className="user-commands">
        <AdminActions buttonClassName="btn-lg mb-4" className='user-admin-actions' database>
          <Link className="btn btn-lg btn-primary mb-4"
            to={reverse(`${routes.listUsers}`)}>Modify Users
          </Link>
          <Link
            className="btn btn-lg btn-primary mb-4"
            to={reverse(`${routes.settingsIndex}`)}
          >Modify Settings
          </Link>
          <Link className="btn btn-lg btn-primary mb-5"
            to={reverse(`${routes.guestLinks}`)}>Guest links
          </Link>
        </AdminActions>
        {user.guest.loggedIn !== true && <Link to={reverse(`${routes.changeUser}`)}
          className="btn btn-lg btn-warning change-user mt-3 mb-5">
          Change password or email address</Link>}
        <Link to={reverse(`${routes.logout}`)}
          className="btn btn-lg btn-primary logout mb-5">Log out</Link>
      </div>
    </div>
  );
}
