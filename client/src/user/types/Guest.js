import PropTypes from 'prop-types';

export const GuestPropType = PropTypes.shape({
    isFetching: PropTypes.bool,
    token: PropTypes.string,
    valid: PropTypes.bool,
    error: PropTypes.string,
    lastUpdated: PropTypes.number,
    username: PropTypes.string,
    password: PropTypes.string,
});