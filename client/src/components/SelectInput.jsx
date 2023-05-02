import React from 'react';
import PropTypes from 'prop-types';

export function SelectInput(props) {
  const { className, formState, hint, label, name,
          register, required, placeholder, type, options } = props;
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
        <label htmlFor={`field-${name}`}>
          {label}
          {required && <span className="required">*</span>}
        </label>
      )}

      <select
        { ...register(name, {required}) }
        placeholder={placeholder || label}
        type={type}
        id={`field-${name}`}
        className={inputClassNames}
      >
        {options.map((opt, idx) => <option key={idx} value={opt}>{opt}</option>)}
    </select>
      {showHint && <small className="form-text text-muted">{hint}</small>}
      {errors[name] && <p className="invalid-feedback">{errors[name]}</p>}
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
