import PropTypes from 'prop-types';

import { UserOptionsPropType } from './UserOptions';

export const UserPropType = PropTypes.shape({
  "pk": PropTypes.number.isRequired,
  "username": PropTypes.string.isRequired,
  "email": PropTypes.string.isRequired,
  "last_login": PropTypes.string,
  "reset_expires": PropTypes.string,
  "reset_token": PropTypes.string,
  "groups": PropTypes.objectOf(PropTypes.bool).isRequired,
  "options": UserOptionsPropType,
  "accessToken": PropTypes.string,
  "refreshToken": PropTypes.string
});