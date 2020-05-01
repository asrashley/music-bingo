import React from 'react';
import PropTypes from 'prop-types';
import DateTimePicker from 'react-datetime-picker';
import { ErrorMessage, Controller } from "react-hook-form";

function DateTimeInput({ className, defaultValue, control, formState, hint, errors, label, name, register, required }) {
  const { dirtyFields, touched } = formState;

  const inputClassNames = [
    'form-control',
    className || '',
    errors[name] ? 'is-invalid' : '',
    (dirtyFields[name] || touched[name]) ? 'is-valid' : '',
  ]
    .join(' ');

  return (
    <div className="form-group">
      {label && (
        <label htmlFor={name}>
          {label}
          {required && <span className="required">*</span>}
        </label>
      )}
      <Controller as={DateTimePicker}
        className={inputClassNames}
        name={name}
        locale="en-gb"
        control={control}
        defaultValue={defaultValue} />
      <small className="form-text text-muted">{hint}</small>
      <ErrorMessage errors={errors} name={name}>
        {({ message }) => <p className="invalid-feedback">{message}</p>}
      </ErrorMessage>
    </div>
  );
}

DateTimeInput.propTypes = {
  className: PropTypes.string,
  control: PropTypes.object.isRequired,
  formState: PropTypes.object.isRequired,
  hint: PropTypes.string,
  errors: PropTypes.object,
  label: PropTypes.string,
  name: PropTypes.string,
  register: PropTypes.func.isRequired,
  required: PropTypes.bool,
};


export {
  DateTimeInput
};
