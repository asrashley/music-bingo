import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import SettingsForm from './SettingsForm';

import { addMessage } from '../../messages/messagesSlice';

import {
  getSettingsIsSaving,
  getSettings,
  getSettingsLastUpdate
} from '../settingsSelectors';
import { getUser } from '../../user/userSelectors';
import { 
  bulkModifySettings,
  fetchSettingsIfNeeded,
  saveModifiedSettings
} from '../settingsSlice';

import { getCurrentSection } from '../settingsSelectors';

import routes from '../../routes';

import '../styles/settings.scss';

class SettingsSectionPage extends React.Component {
  static propTypes = {
    history: PropTypes.object.isRequired,
    lastUpdate: PropTypes.number.isRequired,
    settings: PropTypes.array.isRequired,
    user: PropTypes.object.isRequired
  };

  constructor(props) {
    super(props);
    this.state = {
      values: {},
      lastUpdate: 0
    };
  }

  componentDidMount() {
    const { dispatch } = this.props;
    dispatch(fetchSettingsIfNeeded());
    this.resetValues();
  }

  componentDidUpdate(prevProps, prevState) {
    const { dispatch, lastUpdate, user } = this.props;
    if (user.pk !== prevProps.user.pk) {
      dispatch(fetchSettingsIfNeeded());
    }
    if (lastUpdate !== prevProps.lastUpdate || lastUpdate !== this.state.lastUpdate) {
      this.resetValues();
    }
  }

  render() {
    const { section, settings, user } = this.props;
    const { values } = this.state;
    const isAdmin = (user.groups.admin === true);
    const ready = this.props.lastUpdate === this.state.lastUpdate &&
          this.props.lastUpdate > 0;
    /* the SettingsForm must not be rendered until values is valid, because
      it is only the initial render that will check defaultValues */
    return (
      <div id="settings-page">
      {ready && isAdmin && <SettingsForm
          values={values}
          section={section}
          settings={settings}
          cancel={this.discardChanges}
          submit={this.submit}
          />}
      </div>
    );
  }

  discardChanges = () => {
    const { history } = this.props;
    history.push(`${routes.user}`);
  }

  submit = (section, data) => {
    const { history, settings, dispatch } = this.props;
    const changes = [];
    settings.forEach((field) => {
      let value = data[field.name];
      if (field.type === 'int') {
        value = parseInt(value, 10);
      }
      if (field.value !== value){
        changes.push({
          section,
          field: field.name,
          value
        });
      }
    });
    return new Promise((resolve, reject) => {
      if (changes.length === 0) {
        resolve('No changes to save');
      }
      dispatch(bulkModifySettings(changes));
      dispatch(saveModifiedSettings()).then(() => {
        dispatch(addMessage({ type: 'success', text: `${section} settings saved successfully`}));
        history.push(`${routes.settingsIndex}`);
        resolve(true);
      });
    });
  }

  resetValues = () => {
    const { settings, lastUpdate } = this.props;
    const values = {};
    settings.forEach((field) => {
      values[field.name] = field.value;
    });
    this.setState({
      values,
      lastUpdate
    });
  }
}

const mapStateToProps = (state, ownProps) => {
  return {
    isSaving: getSettingsIsSaving(state, ownProps),
    lastUpdate: getSettingsLastUpdate(state, ownProps),
    settings: getSettings(state, ownProps),
    user: getUser(state, ownProps),
    section: getCurrentSection(state, ownProps),
  };
};

SettingsSectionPage = connect(mapStateToProps)(SettingsSectionPage);
export { SettingsSectionPage };
