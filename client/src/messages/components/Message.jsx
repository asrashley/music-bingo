import React from 'react';
import PropTypes from 'prop-types';

import { DateTime } from '../../components';
import { messageTypes } from '../messagesSlice';

const MessageText = ({ msg }) => {
  let { text } = msg;
  if (!Array.isArray(text)) {
    text = [text];
  }
  return (
    <React.Fragment>
      {msg.heading && <h4 className="alert-heading">{msg.heading}</h4>}
      {text.map((para, key) => <p key={key}>{para}</p>)}
    </React.Fragment>
  );
};

export function Message({ msg, clearMessage}) {
  let classname = `alert alert-dismissible ${messageTypes[msg.type].className}`;
  if (msg.hidden === true) {
    classname += ' fade';
  }

  return (
    <div className={classname} role="alert" id={`msg_${msg.id}`}>
      <button type="button" className="close" data-dismiss="alert" aria-label="Close" onClick={() => clearMessage(msg)}>
        <span aria-hidden="true">&times;</span>
      </button>
      <div className="message-timestamp">
        <DateTime date={msg.timestamp} />
      </div>
      <span className={messageTypes[msg.type].glyph} aria-hidden="true">&nbsp;</span>
      <div className="message-text">
        <MessageText msg={msg} />
      </div>
    </div>
  );
}

Message.propTypes = {
  msg: PropTypes.object.isRequired,
  clearMessage: PropTypes.func.isRequired,
};
