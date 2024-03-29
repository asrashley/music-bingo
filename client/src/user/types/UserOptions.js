import PropTypes from 'prop-types';

export const UserOptionsPropType = PropTypes.shape({
  "colourScheme": PropTypes.string.isRequired,
  "colourSchemes": PropTypes.arrayOf(PropTypes.string),
  "maxTickets": PropTypes.number.isRequired,
  "rows": PropTypes.number.isRequired,
  "columns": PropTypes.number.isRequired
});
