import React from 'react';
import PropTypes from 'prop-types';
import { useForm } from 'react-hook-form';

import SettingsField from './SettingsField';

export default function SettingsForm({ values, section, settings, cancel, submit }) {
  const { register, handleSubmit, formState, setError } = useForm({
    mode: 'onChange',
    defaultValues: values
  });
  const { isSubmitting } = formState;
  const submitWrapper = (data) => {
    console.log(`submitWrapper: ${section} ${JSON.stringify(data)}`);
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
  values: PropTypes.object.isRequired,
  section: PropTypes.string.isRequired,
  settings: PropTypes.array.isRequired,
  cancel: PropTypes.func.isRequired,
  submit: PropTypes.func.isRequired,
};
