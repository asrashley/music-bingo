import { createStore } from '../store/createStore';
import { initialState } from '../store/initialState';
import { messagesSlice } from './messagesSlice';

describe('messagesSlice', () => {
  it('records if fetching directories failed', () => {
    const store = createStore(initialState, false);
    store.dispatch(messagesSlice.actions.addMessage({
      type: 'info',
      timestamp: 1234,
      text: 'an info message'
    }));
    const { messages, nextMessageId } = store.getState().messages;
    expect(messages).toEqual({
      [initialState.messages.nextMessageId]: {
        id: initialState.messages.nextMessageId,
        type: 'info',
        timestamp: 1234,
        text: 'an info message'
      }
    });
    expect(nextMessageId).toEqual(initialState.messages.nextMessageId + 1);
  });

  it('clears a message', () => {
    const initState = {
      ...initialState,
      messages: {
        ...initialState.messages,
        messages: {
          123: {
            id: 123,
            type: 'info',
            timestamp: 1234,
            text: 'an info message'
          }
        },
        nextMessageId: 125,
      }
    };
    const store = createStore(initState, false);
    store.dispatch(messagesSlice.actions.clearMessage({
      id: 5
    }));
    expect(store.getState().messages).toEqual(initState.messages);
    store.dispatch(messagesSlice.actions.clearMessage({
      id: 123
    }));
    expect(store.getState().messages).toEqual({
      ...initState.messages,
      messages: {}
    });
  });

  it('clears a message type', () => {
    const initState = {
      ...initialState,
      messages: {
        ...initialState.messages,
        messages: {
          45: {
            id: 45,
            type: 'info',
            timestamp: 1000,
            text: 'info msg 45'
          },
          62: {
            id: 62,
            type: 'error',
            timestamp: 1200,
            text: 'error msg 62'
          },
          123: {
            id: 123,
            type: 'info',
            timestamp: 1234,
            text: 'an info msg 123'
          }
        },
        nextMessageId: 125,
      }
    };
    const store = createStore(initState, false);
    store.dispatch(messagesSlice.actions.clearMessageType('info'));
    expect(store.getState().messages).toEqual({
      ...initState.messages,
      messages: {
        62: initState.messages.messages[62]
      }
    });
  });

  it('ignores non-500 network errors', () => {
    const store = createStore(initialState, false);
    store.dispatch(messagesSlice.actions.networkError({
      status: 404,
      error: 'Not Found',
      timestamp: 1234,
    }));
    const { messages, nextMessageId } = store.getState().messages;
    expect(messages).toEqual({});
    expect(nextMessageId).toEqual(initialState.messages.nextMessageId);
  });

  it('records a server error', () => {
    const store = createStore(initialState, false);
    store.dispatch(messagesSlice.actions.networkError({
      status: 500,
      error: 'Server error',
      timestamp: 1234,
    }));
    const { messages, nextMessageId } = store.getState().messages;
    expect(messages).toEqual({
      [initialState.messages.nextMessageId]: {
        id: initialState.messages.nextMessageId,
        type: 'error',
        timestamp: 1234,
        heading: "There is a problem with the Musical Bingo service",
        "text": [
          "Please try again later",
          "Server error",
          ],
      }
    });
    expect(nextMessageId).toEqual(initialState.messages.nextMessageId + 1);
  });

});