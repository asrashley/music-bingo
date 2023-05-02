import React, { useEffect, useRef, useState } from 'react';
import PropTypes from 'prop-types';
import { Cell } from 'rsuite-table';

export const EditableTextCell = ({ rowData, dataKey, onChange, className, ...props }) => {
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

  let spanClassName = '';
  if (typeof (className) === 'function') {
    spanClassName = className(rowData);
  } else if (typeof (className) === 'string') {
    spanClassName = className;
  }
  return (
    <Cell {...props}>
      {editing ? (
        <input
          className="input"
          value={value}
          name={dataKey}
          id={`field-${dataKey}`}
          onChange={event => setValue(event.target.value)}
          ref={inputRef}
          onKeyDown={onKeyDown}
        />
      ) : (
        <span
          className={spanClassName}
          onClick={(ev) => setEditing(true)}
        >{rowData[dataKey]}</span>
      )}
    </Cell>
  );
};

EditableTextCell.propTypes = {
  rowData: PropTypes.object.isRequired,
  dataKey: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  className: PropTypes.oneOfType([
    PropTypes.func,
    PropTypes.string
  ]),
};
