import React from 'react';
import PropTypes from 'prop-types';
import { ErrorMessage } from "react-hook-form";

function Input(props) {
  const { className, formState, hint, errors, label, name,
    register, required, placeholder, type } = props;
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

      <input
        name={name}
        ref={register}
        required={required}
        placeholder={placeholder || label}
        type={type}
        className={inputClassNames}
      />
      {showHint && <small className="form-text text-muted">{hint}</small>}
      <ErrorMessage errors={errors} name={name}>
        {({ message }) => <p className="invalid-feedback">{message}</p>}
        </ErrorMessage>
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
}
export {
  Input,
};
