import React, { Suspense, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useDispatch, useSelector } from 'react-redux';

import { fetchSettingsIfNeeded } from '../settings/settingsSlice';
import { fetchUserIfNeeded } from '../user/userSlice';

import { getUser } from '../user/userSelectors';
import { getPrivacySettings } from '../settings/settingsSelectors';

const PrivacyPolicy = React.lazy(() => import('./PrivacyPolicy'));

function LoadingMsg({ text }) {
  return (<div className="loading">Loading {text}...</div>);
}
LoadingMsg.propTypes = {
  text: PropTypes.string.isRequired,
};

export function PrivacyPolicyPage() {
  const settings = useSelector(getPrivacySettings);
  const user = useSelector(getUser);
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(fetchUserIfNeeded());
  }, [dispatch]);

  useEffect(() => {
    dispatch(fetchSettingsIfNeeded(true));
  }, [dispatch, user.pk]);

  if (settings?.valid !== true) {
    return <LoadingMsg text="policy" />;
  }
  return (
    <Suspense fallback={<LoadingMsg text="page" />}>
      <PrivacyPolicy policy={settings} />
    </Suspense>
  );
}
