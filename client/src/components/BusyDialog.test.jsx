import React from 'react';
import { renderWithProviders } from '../testHelpers';
import { fireEvent } from '@testing-library/react';
import { BusyDialog } from './BusyDialog';

describe('BusyDialog component', () => {
  it('renders busy dialog', () => {
    const props = {
      onClose: jest.fn(),
      title: 'Dialog Title',
      text: '49%',
      backdrop: false
    };
    const { getByText, asFragment } = renderWithProviders(<BusyDialog {...props}>
      <div>
        <p>child elements</p>
      </div>
    </BusyDialog>);
    getByText(props.title);
    getByText(props.text);
    getByText('child elements');
    expect(asFragment()).toMatchSnapshot();
  });

  it('calls onClose when cancel is called', () => {
    const props = {
      onClose: jest.fn(),
      title: 'Dialog Title',
      text: '49%',
      backdrop: false
    };
    const { getByText } = renderWithProviders(<BusyDialog {...props} />);
    fireEvent.click(getByText('Cancel'));
    expect(props.onClose).toHaveBeenCalledTimes(1);
  });
});