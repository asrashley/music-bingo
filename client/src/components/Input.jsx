import React from 'react';
import PropTypes from 'prop-types';
import { ErrorMessage } from '@hookform/error-message';

function Input({ className, disabled, formState, hint, label, name,
                 register, required, rules, placeholder, type}) {
  const { dirtyFields, errors, touchedFields } = formState;
  const showHint = true;
  const inputClassNames = [
    'form-control',
    className || '',
    errors[name] ? 'is-invalid' : '',
    (dirtyFields[name] || touchedFields[name]) ? 'is-valid': '',
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

      <input
        { ...register(name, {required, ...rules})}
        placeholder={placeholder || label}
        type={type}
        id={`field-${name}`}
        disabled={disabled}
        className={inputClassNames}
      />
      {showHint && <small className="form-text text-muted">{hint}</small>}
      <ErrorMessage errors={errors} name={name} />
    </div>
  );
}

Input.propTypes = {
  className: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
  formState: PropTypes.object.isRequired,
  erors: PropTypes.object,
  register: PropTypes.func.isRequired,
  required: PropTypes.bool,
  rules: PropTypes.object,
};

export {
  Input,
};
