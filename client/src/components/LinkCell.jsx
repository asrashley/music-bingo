import React from 'react';
import PropTypes from 'prop-types';
import { Cell } from 'rsuite-table';
import { Link } from 'react-router-dom';

export const LinkCell = ({ dataKey, rowData, className, to, ...props }) => {
    let spanClassName = '';
    if (typeof (className) === 'function') {
        spanClassName = className(rowData);
    } else if (typeof (className) === 'string') {
        spanClassName = className;
    }

    return (
        <Cell dataKey={dataKey} {...props}>
            <span className={spanClassName}>
                <Link to={to(rowData)}>{rowData[dataKey]}</Link>
            </span>
        </Cell>
    );
};

LinkCell.propTypes = {
    dataKey: PropTypes.string.isRequired,
    rowData: PropTypes.object.isRequired,
    to: PropTypes.func.isRequired,
    className: PropTypes.oneOfType([
        PropTypes.func,
        PropTypes.string
    ]),
};