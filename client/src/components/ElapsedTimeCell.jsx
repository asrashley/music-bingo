import React from 'react';
import PropTypes from 'prop-types';
import { Cell } from 'rsuite-table';
import { ElapsedTime } from './ElapsedTime';

export const ElapsedTimeCell = ({ dataKey, rowData, className, ...props }) => {
    if (rowData === undefined) {
        return <Cell dataKey={dataKey} {...props} />;
    }

    let spanClassName = '';
    if (typeof (className) === 'function') {
        spanClassName = className(rowData);
    } else if (typeof (className) === 'string') {
        spanClassName = className;
    }

    return (
        <Cell dataKey={dataKey} {...props}>
            <span className={spanClassName}>
                <ElapsedTime date={rowData[dataKey]} />
            </span>
        </Cell>
    );
};

ElapsedTimeCell.propTypes = {
    dataKey: PropTypes.string.isRequired,
    rowData: PropTypes.object,
    className: PropTypes.oneOfType([
        PropTypes.func,
        PropTypes.string
    ]),
};