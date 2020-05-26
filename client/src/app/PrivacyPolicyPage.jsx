import React, { Suspense } from 'react';
import { connect } from 'react-redux';

import { initialState } from './initialState';

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
  let company = process.env.COMPANY;
  if (company) {
    company = JSON.parse(company);
  } else {
      company = {
        name: "Acme",
        email: "privacy@email.address",
        address: "123 Somewhere Street, My Town"
      };
  }
  const dataCenter = process.env.DATACENTER || 'anywhere';
  let informationCommissioner = process.env.INFORMATION_COMMISSIONER;
  if (informationCommissioner) {
    informationCommissioner = JSON.parse(informationCommissioner);
  } else{
    informationCommissioner = {
      link: "https://ico.org.uk/",
      text: "ico.org.uk",
    };
  }
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
