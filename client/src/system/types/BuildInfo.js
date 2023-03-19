import PropTypes from 'prop-types';

export const BuildInfoPropType = PropTypes.shape({
  branch: PropTypes.string.isRequired,
  buildDate: PropTypes.string,
  tags: PropTypes.string,
  version: PropTypes.string.isRequired,
  commit: PropTypes.shape({
    hash: PropTypes.string,
    shortHash: PropTypes.string
  }).isRequired
});
