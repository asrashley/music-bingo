import PropTypes from 'prop-types';

export const GameOptionsPropType = PropTypes.shape({
  backgrounds: PropTypes.array,
  colour_scheme: PropTypes.string.isRequired,
  columns: PropTypes.number.isRequired,
  rows: PropTypes.number.isRequired,
  number_of_cards: PropTypes.number.isRequired,
});
