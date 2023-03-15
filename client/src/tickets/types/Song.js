import PropTypes from 'prop-types';

export const SongPropType = PropTypes.shape({
  "album": PropTypes.string,
  "artist": PropTypes.string,
  "bitrate": PropTypes.number,
  "channels": PropTypes.number,
  "directory": PropTypes.number.isRequired,
  "duration": PropTypes.number.isRequired,
  "filename": PropTypes.string,
  "pk": PropTypes.number.isRequired,
  "sample_rate": PropTypes.number,
  "sample_width": PropTypes.number,
  "title": PropTypes.string.isRequired,
  "uuid": PropTypes.string
});