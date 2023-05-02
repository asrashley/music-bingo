import PropTypes from 'prop-types';
import { ImportTablePropType } from './Importing';

export const ProgressPropType = PropTypes.shape({
  added: PropTypes.arrayOf(ImportTablePropType).isRequired,
  errors: PropTypes.array.isRequired,
  text: PropTypes.string.isRequired,
  pct: PropTypes.number.isRequired,
  phase: PropTypes.number,
  numPhases: PropTypes.number,
  timestamp: PropTypes.number.isRequired,
  filename: PropTypes.string,
  done: PropTypes.bool
});