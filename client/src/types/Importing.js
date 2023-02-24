import PropTypes from 'prop-types';

export const ImportTablePropType = PropTypes.shape({
    count: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired
});

export const ImportingPropType = PropTypes.shape({
  added: PropTypes.arrayOf(ImportTablePropType),
  done: PropTypes.bool,
  errors: PropTypes.arrayOf(PropTypes.string),
  filename: PropTypes.string.isRequired,
  text: PropTypes.string,
  timestamp: PropTypes.number,
  numPhases: PropTypes.number.isRequired,
  pct: PropTypes.number.isRequired,
  phase: PropTypes.number.isRequired,
});
