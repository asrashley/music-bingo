import React from 'react';
import PropTypes from 'prop-types';
import { Cell } from 'rsuite-table';

export const TextCell = ({ dataKey, rowData, className, ...props }) => {
  let spanClassName = '';
  if (typeof (className) === 'function') {
    spanClassName = className(rowData);
  } else if (typeof (className) === 'string') {
    spanClassName = className;
  }

  return (
    <Cell dataKey={dataKey} {...props}>
      <span className={spanClassName}>
        {rowData[dataKey]}
      </span>
    </Cell>
  );
};

TextCell.propTypes = {
  dataKey: PropTypes.string.isRequired,
  rowData: PropTypes.object.isRequired,
  className: PropTypes.oneOfType([
    PropTypes.func,
    PropTypes.string
  ]),
};