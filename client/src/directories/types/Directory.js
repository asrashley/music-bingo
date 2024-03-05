import PropTypes from 'prop-types';

import { SongPropType } from '../../tickets/types/Song';

const DirectoryShape = {
  parent: PropTypes.number,
  pk: PropTypes.number.isRequired,
  title: PropTypes.string.isRequired,
  songs: PropTypes.arrayOf(SongPropType),
  lastUpdated: PropTypes.number,
  isFetching: PropTypes.bool,
  didInvalidate: PropTypes.bool,
  invalid: PropTypes.bool,
  exists: PropTypes.bool,
  expanded: PropTypes.bool
};
DirectoryShape.directories = PropTypes.arrayOf(PropTypes.shape(DirectoryShape));

export const DirectoryPropType = PropTypes.shape(DirectoryShape);
