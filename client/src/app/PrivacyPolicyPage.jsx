import React, { Suspense } from 'react';
import { connect } from 'react-redux';

import { initialState } from './initialState';
import { company, dataCenter, informationCommissioner } from './privacySettings';

const PrivacyPolicy = React.lazy(() => import('./PrivacyPolicy'));


class PrivacyPolicyPage extends React.Component {
  render() {
    return (
      <Suspense fallback={<div className="loading">Loading...</div>}>
      <PrivacyPolicy {...this.props} />
      </Suspense>
    );
  };
}

const mapStateToProps = (state, ownProps) => {
  state = state || initialState;
  return {
    company,
    dataCenter,
    informationCommissioner,
  };
};

PrivacyPolicyPage = connect(mapStateToProps)(PrivacyPolicyPage);

export {
  PrivacyPolicyPage
};
