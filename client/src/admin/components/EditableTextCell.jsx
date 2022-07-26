import React, { useEffect, useRef, useState } from 'react';
import PropTypes from 'prop-types';
import { Cell } from 'rsuite-table';

export const EditableTextCell = ({ rowData, dataKey, onChange, ...props }) => {
  const [value, setValue] = useState(rowData[dataKey]);
  const inputRef = useRef(null);
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    if (editing) {
      inputRef.current.focus();
    }
  }, [editing]);

  const onKeyDown = (ev) => {
    if (ev.key === 'Enter') {
      onChange({ rowData, dataKey, value });
      setEditing(false);
    } else if (ev.key === 'Escape') {
      setEditing(false);
      setValue(rowData[dataKey]);
    }
  };
  return (
    <Cell {...props}>
      {editing ? (
        <input
          className="input"
          value={value}
          onChange={event => setValue(event.target.value)}
          ref={inputRef}
          onKeyDown={onKeyDown}
        />
      ) : (
        <span
          className={rowData.modified ? 'modified' : ''}
          onClick={(ev) => setEditing(true)}
        >{rowData[dataKey]}</span>
      )}
    </Cell>
  );
};

EditableTextCell.propTypes = {
  rowData: PropTypes.object.isRequired,
  dataKey: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired
};
