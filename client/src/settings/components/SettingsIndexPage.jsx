import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { reverse } from 'named-urls';

/* actions */
import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchSettingsIfNeeded } from '../../settings/settingsSlice';

/* selectors */
import { getUser } from '../../user/userSelectors';
import { getSettingsSections } from '../../settings/settingsSelectors';

/* data */
import { routes } from '../../routes/routes';

import '../styles/settings.scss';

export function SettingsIndexPage() {
  const dispatch = useDispatch();
  const user = useSelector(getUser);
  const settingsSections = useSelector(getSettingsSections);

  useEffect(() => {
    dispatch(fetchUserIfNeeded());
  }, [dispatch]);

  useEffect(() => {
    if (user.loggedIn) {
      dispatch(fetchSettingsIfNeeded('all'));
    }
  }, [dispatch, user]);

  if (user.groups.admin !== true) {
    return (
      <div id="settings-page">
        <div className="alert alert-warning" role="alert">
          <span className="error-message">Only an admin can modify settings</span>
        </div>
      </div>
    );
  }

  return (
    <div id="settings-page">
      <div className="user-commands">
        {settingsSections.map((section) => <Link
          className="btn btn-lg btn-primary mb-4"
          to={reverse(`${routes.settingsSection}`, { section })}
          key={section}
        >Modify {section} Settings
        </Link>)}
      </div>
    </div >
  );
}
