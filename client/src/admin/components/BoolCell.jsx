import React from 'react';
import PropTypes from 'prop-types';
import { Cell } from 'rsuite-table';

export const BoolCell = ({ group, onClick, rowData, className, ...props }) => {
  const cell = rowData.groups[group];
  const icon = (cell === true) ?
    <span className="bool-cell group-true">&#x2714;</span> :
    <span className="bool-cell group-false">&#x2718;</span>;
  let btnClassName = '';
  if (typeof (className) === 'function') {
    btnClassName = className(rowData);
  } else if (typeof (className) === 'string') {
    btnClassName = className;
  }

  return (
    <Cell {...props}>
      <button
        className={btnClassName}
        disabled={rowData.deleted === true}
        onClick={() => onClick({ value: cell === true, group, user: rowData })}
      >{icon}</button>
    </Cell>
  );
};

BoolCell.propTypes = {
  group: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
  rowData: PropTypes.object.isRequired
};
