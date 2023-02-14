import PropTypes from 'prop-types';

export const GitInfoType = PropTypes.shape({
  branch: PropTypes.string.isRequired,
  buildDate: PropTypes.string,
  tags: PropTypes.string,
  commit: PropTypes.shape({
    hash: PropTypes.string,
    shortHash: PropTypes.string
  }).isRequired
});
