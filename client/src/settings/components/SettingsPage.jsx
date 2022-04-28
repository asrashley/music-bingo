import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { useForm } from 'react-hook-form';

import { initialState } from '../../app/initialState';

import { Input, SelectInput } from '../../components';

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

import routes from '../../routes';

import '../styles/settings.scss';

function SettingsField({
  field, formState, isSubmitting, register
}) {
  const { help, name, title, type } = field;
  const rules = {
    validate: {}
  };
  let inputType="text";
  if (type === 'int') {
    inputType = 'number';
    rules.validate = {
      minValue: (v) => (field.minValue === null || v >= field.minValue) || `Minimum value is ${field.minValue}`,
      maxValue: (v) => (field.maxValue === null || v <= field.maxValue) || `Maximum value is ${field.maxValue}`
    };
  } else if (type === 'bool') {
    inputType = 'checkbox';
  }

  return (
    <div className={`border settings-field ${name}`}>
      <div className="setting-name">{title}</div>
      <div className="setting-edit">
        {(type==='enum') ? (
        <SelectInput
          name={name}
          type="text"
          hint={help}
          register={register}
          formState={formState}
          options={field.choices}
          disabled={isSubmitting}
        />
    ):(
        <Input
          name={name}
          type={inputType}
          hint={help}
          register={register}
          rules={rules}
          formState={formState}
          disabled={isSubmitting}
        />
    )}
      </div>
    </div>
  );
}

function SettingsForm({values, settings, cancel, submit}) {
  const { register, handleSubmit, formState, setError } = useForm({
    mode: 'onChange',
    defaultValues: values
  });
  const { isSubmitting } = formState;
  const submitWrapper = (data) => {
    console.log(`submitWrapper: ${JSON.stringify(data)}`);
    return submit(data)
      .then(result => {
        if (result !== true) {
          setError(result);
        }
      })
      .catch(err => {
        setError(`${err}`);
      });
  };
  return (
    <form onSubmit={handleSubmit(submitWrapper)}>
      {settings.map((field, idx) => (
        <SettingsField
          field={field}
          formState={formState}
          key={idx}
          register={register}
        />
      ))}
      <div className="clearfix">
        <button type="submit" className="btn btn-success login-button mr-4"
                disabled={isSubmitting}>Save Changes</button>
        <button className="btn btn-warning mr-4" disabled={isSubmitting}
                onClick={cancel}>Discard Changes</button>
      </div>
    </form>
  );
}

class SettingsPage extends React.Component {
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
    const { settings, user } = this.props;
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

/*  changeSetting = (change) => {
    const { values } = this.state;
    console.log(`changeSetting ${JSON.stringify(change)}`);
    this.setState({
      values: {
        ...values,
        ...change
      }
    });
  }*/

  submit = (data) => {
    const { history, settings, dispatch } = this.props;
    const changes = [];
    console.dir(data);
    settings.forEach((field) => {
      let value = data[field.name];
      if (field.type === 'int') {
        value = parseInt(value, 10);
      }
      console.log(`${field.name} type=${field.type} value="${field.value}" data="${value}"`);
      if (field.value !== value){
        changes.push({
          field: field.name,
          value
        });
      }
    });
    console.dir(changes);
    return new Promise((resolve, reject) => {
      if (changes.length === 0) {
        resolve('No changes to save');
      }
      dispatch(bulkModifySettings(changes));
      dispatch(saveModifiedSettings()).then((result) => {
        console.dir(result);
        history.push(`${routes.user}`);
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
  state = state || initialState;
  return {
    isSaving: getSettingsIsSaving(state, ownProps),
    lastUpdate: getSettingsLastUpdate(state, ownProps),
    settings: getSettings(state, ownProps),
    user: getUser(state, ownProps),
  };
};

SettingsPage = connect(mapStateToProps)(SettingsPage);
export { SettingsPage };
