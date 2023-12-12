import React from 'react';
import PropTypes from 'prop-types';
import { Cell } from 'rsuite-table';

export const SelectCell = ({ onClick, rowData, className, ...props }) => (
  <Cell {...props}>
    <input
      type="checkbox"
      name={`sel-${rowData?.pk}`}
      onChange={ev => onClick({ rowData, checked: !rowData?.selected })}
      checked={rowData?.selected}
    />
  </Cell>);

SelectCell.propTypes = {
  rowData: PropTypes.object,
  onClick: PropTypes.func.isRequired,
  className: PropTypes.oneOfType([
    PropTypes.func,
    PropTypes.string
  ]),
};
