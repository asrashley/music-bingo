import PropTypes from 'prop-types';

import { CellPropType } from './Cell';

export const TicketPropType = PropTypes.shape({
  pk: PropTypes.number.isRequired,
  number: PropTypes.number.isRequired,
  game: PropTypes.number.isRequired,
  rows: PropTypes.arrayOf(PropTypes.arrayOf(CellPropType)),
  title: PropTypes.string.isRequired,
  tracks: PropTypes.array,
  checked: PropTypes.number,
  user: PropTypes.number, /* pk of user */
  lastUpdated: PropTypes.number,
  error: PropTypes.string
});