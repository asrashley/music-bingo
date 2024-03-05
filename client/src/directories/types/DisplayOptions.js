import PropTypes from 'prop-types';

export const DisplayOptionsPropType = PropTypes.shape({
    ascending: PropTypes.bool,
    field: PropTypes.string,
    onlyExisting: PropTypes.bool,
});
