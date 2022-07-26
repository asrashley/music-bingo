import React from 'react';
import PropTypes from 'prop-types';
import { Cell } from 'rsuite-table';

export const SelectCell = ({ onClick, rowData, ...props }) => (
  <Cell {...props}>
    <input
      type="checkbox"
      name={`sel-${rowData.pk}`}
      onChange={ev => onClick({ rowData, value: ev.target.value })}
      checked={rowData.selected}
    />
  </Cell>
);
SelectCell.propTypes = {
  rowData: PropTypes.object.isRequired,
  onClick: PropTypes.func.isRequired
};
