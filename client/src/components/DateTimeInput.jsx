import React from 'react';
import PropTypes from 'prop-types';
import DateTimePicker from 'react-datetime-picker';

class DateTimeInput extends React.Component {
  static propTypes = {
    input: PropTypes.object.isRequired,
    label: PropTypes.string,
  };

  render() {
    const { input, label, meta, hint, required, className } = this.props;
    const { error, warning } = meta;
    const { name, onChange } = input;
    let { value } = input;
    const valid = !error;
    const showHint = hint && !(error || warning);

    if (typeof (value) === "string") {
      if (value) {
        value = new Date(value);
      } else {
        value = null; // new Date();
      }
      
    }
    const inputClassNames = [
      'form-control',
      className,
      error ? 'is-invalid' : '',
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

        <DateTimePicker
          onChange={onChange}
          name={name}
          value={value}
          required={required}
          locale="en-gb"
          className={inputClassNames}
        />
        {showHint && <small className="form-text text-muted">{hint}</small>}
        {error && <div className="invalid-feedback">{error}</div>}
        {warning && <div className="form-text text-muted">{warning}</div>}
      </div>
    );
  }
}

export {
  DateTimeInput
};
