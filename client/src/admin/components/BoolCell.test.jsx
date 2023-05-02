import React from 'react';
import { fireEvent } from '@testing-library/react';

import { renderWithProviders } from '../../testHelpers';
import { BoolCell } from './BoolCell';

describe('BoolCell component', () => {
  it('renders bool cell', () => {
    const onClick = jest.fn();
    const rowData = {
      groups: {
        users: true,
        creators: true,
        hosts: true,
        admin: false
      }
    };
    const className = 'btn-class-name';
    const { rerender, getBySelector, asFragment } = renderWithProviders(
      <BoolCell group="users" onClick={onClick} rowData={rowData} className={className} />);
    getBySelector('.group-true');
    getBySelector(`button.${className}`);
    expect(asFragment()).toMatchSnapshot();
    rerender(<BoolCell group="admin" onClick={onClick} rowData={rowData} className={className} />);
    getBySelector('.group-false');
  });

  it('calls onClick when button is clicked', () => {
    const group = 'users';
    const onClick = jest.fn();
    const rowData = {
      groups: {
        users: true,
        creators: true,
        hosts: true,
        admin: false
      }
    };
    const className = 'btn-class-name';
    const { getBySelector} = renderWithProviders(
      <BoolCell group={group} onClick={onClick} rowData={rowData} className={className} />);
    fireEvent.click(getBySelector('button'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('supports a function as classname', () => {
    const group = 'users';
    const onClick = jest.fn();
    const rowData = {
      groups: {
        users: true,
        creators: true,
        hosts: true,
        admin: false
      }
    };
    const className = () => 'fn-class-name';
    const { getBySelector } = renderWithProviders(
      <BoolCell group={group} onClick={onClick} rowData={rowData} className={className} />);
    getBySelector('button.fn-class-name');
  });
});
