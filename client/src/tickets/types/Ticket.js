import PropTypes from 'prop-types';

export const TicketPropTypes = PropTypes.shape({
  pk: PropTypes.number.isRequired,
  number: PropTypes.number.isRequired,
  game: PropTypes.number.isRequired,
  title: PropTypes.string.isRequired,
  tracks: PropTypes.array,
  checked: PropTypes.number,
  user: PropTypes.number, /* pk of user */
  lastUpdated: PropTypes.number,
});