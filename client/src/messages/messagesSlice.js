import { createSlice } from '@reduxjs/toolkit';

import { api } from '../endpoints';

export const messageTypes = {
  'success': {
    className: "alert-success",
    glyph: 'glyphicon glyphicon-ok-sign'
  },
  'info': {
    className: "alert-info",
    glyph: 'glyphicon glyphicon-info-sign',
  },
  'error': {
    className: "alert-danger",
    glyph: 'glyphicon glyphicon-exclamation-sign',
  }
}

export const messagesSlice = createSlice({
  name: 'messages',
  initialState: {
    messages: {},
    duration: 15000,
    nextMessageId: 1,
  },
  reducers: {
    addMessage: (state, action) => {
      const { type, text } = action.payload;
      let { timestamp } = action.payload;
      if (timestamp === undefined) {
        timestamp = Date.now();
      }
      const msg = {
        id: state.nextMessageId,
        type,
        text,
        timestamp,
      };
      state.nextMessageId++;
      state.messages[msg.id] = msg;
    },
    clearMessage: (state, action) => {
      const msg = action.payload;
      if (msg && msg.id in state.messages) {
        delete state.messages[msg.id];
      }
    },
    networkError: (state, action) => {
      const { error, timestamp } = action.payload;
      const msg = {
        type: 'error',
        heading: 'There is a problem with the Musical Bingo service',
        text: ['Please try again later', error],
        id: state.nextMessageId,
        timestamp
      };
      state.nextMessageId++;
      state.messages[msg.id] = msg;
    }
  }
});

export const { addMessage, clearMessage } = messagesSlice.actions;

export const initialState = messagesSlice.initialState;

export default messagesSlice.reducer;

api.actions.networkError = messagesSlice.actions.networkError;
