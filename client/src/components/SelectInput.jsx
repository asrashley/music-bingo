import React from 'react';
import PropTypes from 'prop-types';
import { ErrorMessage } from "react-hook-form";

export function SelectInput(props) {
  const { className, formState, hint, errors, label, name,
          register, required, placeholder, type, options } = props;
  const { dirtyFields, touched } = formState;
  const showHint = true;
  const inputClassNames = [
    'form-control',
    className || '',
    errors[name] ? 'is-invalid' : '',
    (dirtyFields[name] || touched[name]) ? 'is-valid': '',
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

      <select
        name={name}
        ref={register}
        required={required}
        placeholder={placeholder || label}
        type={type}
        className={inputClassNames}
      >
        {options.map((opt, idx) => <option key={idx} value={opt}>{opt}</option>)}
    </select>
      {showHint && <small className="form-text text-muted">{hint}</small>}
      <ErrorMessage errors={errors} name={name}>
        {({ message }) => <p className="invalid-feedback">{message}</p>}
        </ErrorMessage>
    </div>
  );
}

SelectInput.propTypes = {
  className: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  options: PropTypes.array.isRequired,
  formState: PropTypes.object.isRequired,
  erors: PropTypes.object,
  register: PropTypes.func.isRequired,
};
