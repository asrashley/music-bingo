import React from 'react';
import PropTypes from 'prop-types';
import { useForm } from 'react-hook-form';

import SettingsField from './SettingsField';
import { SettingsFieldPropType } from '../types/SettingsField';

export default function SettingsForm({ values, section, settings, cancel, submit }) {
  const { register, handleSubmit, formState, setError } = useForm({
    mode: 'onChange',
    defaultValues: values
  });
  const { isSubmitting } = formState;
  const submitWrapper = (data) => {
    return submit(section, data)
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

SettingsForm.propTypes = {
  values: PropTypes.objectOf(
    PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.number,
      PropTypes.bool
  ])),
  section: PropTypes.string.isRequired,
  settings: PropTypes.arrayOf(SettingsFieldPropType).isRequired,
  cancel: PropTypes.func.isRequired,
  submit: PropTypes.func.isRequired,
};
