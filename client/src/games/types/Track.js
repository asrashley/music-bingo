import PropTypes from 'prop-types';

export const TrackPropType = PropTypes.shape({
  number: PropTypes.number.isRequired,
  start_time: PropTypes.number.isRequired,
  duration: PropTypes.number.isRequired,
  title: PropTypes.string.isRequired,
  artist: PropTypes.string.isRequired,
  album: PropTypes.string.isRequired,
});
