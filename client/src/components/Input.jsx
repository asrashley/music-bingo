import React from 'react';
import PropTypes from 'prop-types';
import { ErrorMessage } from '@hookform/error-message';

function Input({ className, disabled, formState, groupClassName = 'form-group', hint, label, name,
  register, required, rules, placeholder, type }) {
  const { dirtyFields, errors, touchedFields } = formState;
  const showHint = hint !== undefined;
  const inputClassNames = [
    'form-control',
    className || '',
    errors[name] ? 'is-invalid' : '',
    (dirtyFields[name] || touchedFields[name]) ? 'is-valid' : '',
  ]
    .join(' ');

  return (
    <div className={groupClassName}>
      {label && (
        <label htmlFor={`field-${name}`}>
          {label}
          {required && <span className="required">*</span>}
        </label>
      )}

      <input
        {...register(name, { required, ...rules })}
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
  disabled: PropTypes.bool,
  formState: PropTypes.object.isRequired,
  groupClassName: PropTypes.string,
  hint: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  register: PropTypes.func.isRequired,
  required: PropTypes.bool,
  rules: PropTypes.object,
  type: PropTypes.string.isRequired,
};

export {
  Input,
};
