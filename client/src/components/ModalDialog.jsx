import React from 'react';
import PropTypes from 'prop-types';

export const ModalDialog = ({ id, onCancel, title, timestamp = 0, className, footerClassName, children, footer }) => {
    return (
        <div
            className={`modal show dialog-active ${className || ''}`}
            tabIndex="-1"
            data-last-update={timestamp}
            style={{ display: "block" }}
            role="dialog">
            <div className="modal-dialog" role="document" id={id || 'dialogbox'}>
                <div className="modal-content">
                    <div className="modal-header">
                        <h5 className="modal-title">{title}</h5>
                        <button type="button" className="close" data-dismiss="modal" aria-label="Close" onClick={onCancel}>
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div className="modal-body">
                        {children}
                    </div>
                    <div className={`modal-footer ${footerClassName || ''}`}>
                        {footer}
                    </div>
                </div>
            </div>
        </div>
    );
};

ModalDialog.propTypes = {
    children: PropTypes.node,
    className: PropTypes.string,
    footerClassName: PropTypes.string,
    id: PropTypes.string,
    footer: PropTypes.node,
    onCancel: PropTypes.func.isRequired,
    timestamp: PropTypes.number,
    title: PropTypes.node.isRequired
};
