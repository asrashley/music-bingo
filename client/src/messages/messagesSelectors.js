import { createSelector } from 'reselect';

const getMsgMap = (state) => state.messages.messages;

const timestampOrder = (a, b) => {
  return a.timestamp - b.timestamp;
};

export const getMessages = createSelector([getMsgMap],
  (msgMap) => {
    const messages = [];
    for (let id in msgMap) {
      messages.push(msgMap[id]);
    }
    messages.sort(timestampOrder);
    return messages;
  });
