import React from 'react';
import PropTypes from 'prop-types';

export function ErrorMessage({ error }) {
  if (!error) {
    return null;
  }
  return (
    <div className="alert alert-warning" role="alert">
      <span className="error-message">{error}</span>
    </div>
  );
}
ErrorMessage.propTypes = {
  error: PropTypes.string
};
