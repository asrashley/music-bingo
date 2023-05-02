import { createSlice } from '@reduxjs/toolkit';

import { userChangeListeners } from '../user/userSlice';

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

export const initialState = {
  messages: {},
  duration: 15000,
  nextMessageId: 1,
};

export const messagesSlice = createSlice({
  name: 'messages',
  initialState,
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
    clearMessageType: (state, action) => {
      const type = action.payload;
      const before = Date.now() - 2000;
      for (let id in state.messages) {
        const msg = state.messages[id];
        if (msg.type === type && msg.timestamp < before) {
          delete state.messages[id];
        }
      }
    },
    networkError: (state, action) => {
      const { status, error, timestamp } = action.payload;
      if (status >= 500) {
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
    },
    receiveUser: (state) => {
      state.messages = {};
    }
  }
});

export const { addMessage, clearMessage, clearMessageType } = messagesSlice.actions;

export default messagesSlice.reducer;

api.actions.networkError = messagesSlice.actions.networkError;

userChangeListeners.receive.messages = messagesSlice.actions.receiveUser;
