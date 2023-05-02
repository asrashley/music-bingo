import React, { Suspense } from 'react';
import { connect } from 'react-redux';

import { fetchSettingsIfNeeded } from '../settings/settingsSlice';
import { fetchUserIfNeeded } from '../user/userSlice';

import { getUser } from '../user/userSelectors';
import { getPrivacySettings } from '../settings/settingsSelectors';

const PrivacyPolicy = React.lazy(() => import('./PrivacyPolicy'));

function LoadingMsg({ text }) {
  return (<div className="loading">Loading {text}...</div>);
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
    if (settings?.valid !== true) {
      return <LoadingMsg text="policy"/>;
    }
    return (
      <Suspense fallback={<LoadingMsg text="page"/>}>
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
