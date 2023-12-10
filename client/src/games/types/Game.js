import PropTypes from 'prop-types';

import { GameOptionsPropType } from './GameOptions';
import { TrackPropType } from './Track';

export const GamePropType = PropTypes.shape({
  end: PropTypes.string.isRequired,
  id: PropTypes.string.isRequired,
  pk: PropTypes.number.isRequired,
  start: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  slug: PropTypes.string.isRequired,
  options: GameOptionsPropType,
  userCount: PropTypes.number,
  tracks: PropTypes.arrayOf(TrackPropType),
  ticketOrder: PropTypes.arrayOf(PropTypes.number),
  isFetchingDetail: PropTypes.bool,
  invalidDetail: PropTypes.bool,
  lastUpdated: PropTypes.number,
  isModifying: PropTypes.bool,
  round: PropTypes.number,
  firstGameOfTheDay: PropTypes.bool,
});
