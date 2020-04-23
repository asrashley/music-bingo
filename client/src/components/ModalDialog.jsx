import React from 'react';
import PropTypes from 'prop-types';

export const ModalDialog = ({ id, onCancel, title, className, footerClassName, children, footer }) => {
    return (
        <div
            className={`modal show dialog-active ${className || ''}`}
            tabIndex="-1" style={{ display: "block" }}
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
    className: PropTypes.string,
    footerClassName: PropTypes.string,
    id: PropTypes.string,
    onCancel: PropTypes.func.isRequired,
    title: PropTypes.node.isRequired
};