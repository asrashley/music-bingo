import PropTypes from 'prop-types';

export const CellPropType = PropTypes.shape({
  title: PropTypes.string.isRequired,
  artist: PropTypes.string,
  background: PropTypes.string,
  checked: PropTypes.bool
});