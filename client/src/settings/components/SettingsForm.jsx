import React, { useCallback, useState } from 'react';
import PropTypes from 'prop-types';
import { useForm } from 'react-hook-form';

import SettingsField from './SettingsField';
import { SettingsFieldPropType } from '../types/SettingsField';

export default function SettingsForm({ values, section, settings, cancel, submit }) {
  const { register, handleSubmit, formState } = useForm({
    mode: 'onChange',
    defaultValues: values
  });
  const [ error, setError] = useState(null);
  const { isSubmitting } = formState;
  const submitWrapper = useCallback((data) => {
    setError(null);
    return submit(section, data)
      .then(result => {
        if (result !== true && result !== undefined) {
          setError(result);
        }
      })
      .catch(err => {
        setError(`${err}`);
      });
  }, [section, submit]);

  return (
    <form onSubmit={handleSubmit(submitWrapper)}>
      {error !== null && <div className="alert alert-warning" role="alert"><span className="error-message">{error}</span></div>}
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
