import React from 'react';
import PropTypes from 'prop-types';
import DateTimePicker from 'react-datetime-picker';
import { Controller } from "react-hook-form";

function RenderPicker({name, required}) {
  return ({field}) => {
    const { onChange, value, name } = field;
    return <DateTimePicker
             onChange={onChange}
             value={value}
             name={name}
             required={required}
             locale="en-gb"
           />;
  };
}

function DateTimeInput({ className, control, formState, hint, label, name, register, required }) {
  const { dirtyFields, errors, touchedFields } = formState;

  const inputClassNames = [
    'form-control',
    className || '',
    errors[name] ? 'is-invalid' : '',
    (dirtyFields[name] || touchedFields[name]) ? 'is-valid' : '',
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
      <Controller
        render={RenderPicker({name, required})}
        className={inputClassNames}
        name={name}
        rules={{required}}
        control={control}
      />
      <small className="form-text text-muted">{hint}</small>
      {errors[name] && <p className="invalid-feedback">{errors[name]}</p>}
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
