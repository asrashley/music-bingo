import React from 'react';
import PropTypes from 'prop-types';

class Input extends React.Component {
  static propTypes = {
    input: PropTypes.object.isRequired,
    label: PropTypes.string,
  };

  render() {
    const { input, label, type, meta, hint, required, className } = this.props;
    const { touched, error, warning } = meta;
    const { name } = input;
    const valid = touched && !error;
    const showHint = hint && !(touched && (error || warning));

    const inputClassNames = [
      'form-control',
      className,
      (touched && error) ? 'is-invalid' : '',
      valid ? 'is-valid': '',
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
          {...input}
          valid={valid.toString()}
          required={required}
          placeholder={label}
          type={type}
          className={inputClassNames}
        />

        {showHint && <small className="form-text text-muted">{hint}</small>}

        {touched && (
          (error && <div className="invalid-feedback">{error}</div>) ||
          (warning && <div className="form-text text-muted">{warning}</div>)
        )}
      </div>
    );
  }
}

export {
  Input
};
