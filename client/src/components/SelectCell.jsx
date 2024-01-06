import React from 'react';
import PropTypes from 'prop-types';
import { Cell } from 'rsuite-table';

export function SelectCell({ onClick, rowData, className, ...props }) {
  let inpClassName = '';
  if (className) {
    inpClassName = typeof (className) === 'function' ? className(rowData) : className;
  }
  return (<Cell {...props}>
    <input
      type="checkbox"
      className={inpClassName}
      name={`sel-${rowData?.pk}`}
      onChange={() => onClick({ rowData, checked: !rowData?.selected })}
      checked={rowData?.selected}
    />
  </Cell>);
}

SelectCell.propTypes = {
  rowData: PropTypes.object,
  onClick: PropTypes.func.isRequired,
  className: PropTypes.oneOfType([
    PropTypes.func,
    PropTypes.string
  ]),
};
