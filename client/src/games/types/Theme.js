import PropTypes from 'prop-types';

export const ThemePropType = PropTypes.shape({
  title: PropTypes.string.isRequired,
  count: PropTypes.number.isRequired,
  maxCount: PropTypes.number.isRequired
});

