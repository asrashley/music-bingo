import { ROUTER_ON_LOCATION_CHANGED } from '@lagunovsky/redux-react-router';

import { clearMessageType } from './messagesSlice';

const messagesMiddleware = store => next => action => {
  if (action?.type !== ROUTER_ON_LOCATION_CHANGED) {
    return next(action);
  }
  const { dispatch } = store;
  dispatch(clearMessageType('success'));
  return next(action);
};

export default messagesMiddleware;