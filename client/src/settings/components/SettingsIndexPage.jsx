import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { connect } from 'react-redux';
import { reverse } from 'named-urls';

/* actions */
import { fetchUserIfNeeded } from '../../user/userSlice';
import { fetchSettingsIfNeeded } from '../../settings/settingsSlice';

/* selectors */
import { getUser } from '../../user/userSelectors';
import { getSettingsSections } from '../../settings/settingsSelectors';

/* data */
import routes from '../../routes';

/* PropTypes */

import { UserPropType } from '../../user/types/User';

import '../styles/settings.scss';

class SettingsIndexPageComponent extends React.Component {
  static propTypes = {
    dispatch: PropTypes.func.isRequired,
    settingsSections: PropTypes.arrayOf(PropTypes.string).isRequired,
    user: UserPropType.isRequired,
  };

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
    const { user, settingsSections } = this.props;
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
}

const mapStateToProps = (state, props) => {
  return {
    user: getUser(state, props),
    settingsSections: getSettingsSections(state),
  };
};

const SettingsIndexPage = connect(mapStateToProps)(SettingsIndexPageComponent);

export { SettingsIndexPage, SettingsIndexPageComponent };
