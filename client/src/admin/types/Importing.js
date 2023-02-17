import PropTypes from 'prop-types';

export const ImportingPropType = PropTypes.shape({
  added: PropTypes.object,
  done: PropTypes.bool,
  errors: PropTypes.arrayOf(PropTypes.string),
  filename: PropTypes.string.isRequired,
  text: PropTypes.string,
  timestamp: PropTypes.number,
  numPhases: PropTypes.number.isRequired,
  pct: PropTypes.number.isRequired,
  phase: PropTypes.number.isRequired,
});