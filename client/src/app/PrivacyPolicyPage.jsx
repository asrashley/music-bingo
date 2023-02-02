import React, { Suspense } from 'react';
import { connect } from 'react-redux';

import { fetchSettingsIfNeeded } from '../settings/settingsSlice';
import { fetchUserIfNeeded } from '../user/userSlice';

import { getUser } from '../user/userSelectors';
import { getPrivacySettings } from '../settings/settingsSelectors';

const PrivacyPolicy = React.lazy(() => import('./PrivacyPolicy'));

function LoadingMsg() {
  return (<div className="loading">Loading...</div>);
}

class PrivacyPolicyPage extends React.Component {
  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(fetchUserIfNeeded());
    dispatch(fetchSettingsIfNeeded());
  }

  componentDidUpdate(prevProps, prevState) {
    const { dispatch, user } = this.props;
    if (prevProps.user.pk !== user.pk) {
      dispatch(fetchSettingsIfNeeded());
    }
  }

  render() {
    const { settings } = this.props;
    console.dir(settings);
    if (settings?.valid !== true) {
      return <LoadingMsg />;
    }
    return (
      <Suspense fallback={LoadingMsg}>
        <PrivacyPolicy policy={settings} />
      </Suspense>
    );
  };
}

const mapStateToProps = (state, ownProps) => {
  return {
    settings: getPrivacySettings(state, ownProps),
    user: getUser(state, ownProps),
  };
};

PrivacyPolicyPage = connect(mapStateToProps)(PrivacyPolicyPage);

export {
  PrivacyPolicyPage
};
