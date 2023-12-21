import { LOCATION_CHANGE } from 'connected-react-router';

import { clearMessageType } from './messagesSlice';

const messagesMiddleware = store => next => action => {
  if (action?.type !== LOCATION_CHANGE) {
    return next(action);
  }
  const { dispatch } = store;
  dispatch(clearMessageType('success'));
  return next(action);
};

export default messagesMiddleware;