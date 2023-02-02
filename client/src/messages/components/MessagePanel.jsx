import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import { Message } from './Message';
import { clearMessage } from '../messagesSlice';
import { getMessages } from '../messagesSelectors';

import '../styles/messages.scss';

class MessagePanel extends React.Component {
  static propTypes = {
    messages: PropTypes.array.isRequired,
    dispatch: PropTypes.func.isRequired,
  };

  clearMessage = (msg) => {
    const { dispatch } = this.props;
    dispatch(clearMessage(msg));
  }

  render() {
    const { messages } = this.props;
    return (
      <div id="message-panel" >
        {messages.map((msg, key) => <Message key={key} msg={msg} clearMessage={this.clearMessage}/>)}
      </div>
    );
  }
}

const mapStateToProps = (state, props) => {
  return {
    messages: getMessages(state, props),
  };
};

MessagePanel = connect(mapStateToProps)(MessagePanel);

export {
  MessagePanel
};
