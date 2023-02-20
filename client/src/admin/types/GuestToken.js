import PropTypes from 'prop-types';

export const GuestTokenPropType = PropTypes.shape({
  "pk": PropTypes.number.isRequired,
  "jti": PropTypes.string.isRequired,
  "token_type": PropTypes.number.isRequired,
  "username": PropTypes.string.isRequired,
  "created": PropTypes.string.isRequired,
  "expires": PropTypes.string.isRequired,
  "revoked": PropTypes.bool
});