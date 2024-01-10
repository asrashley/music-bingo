import React from 'react';
import { renderWithProviders } from '../../tests';
import { fireEvent } from '@testing-library/react';
import { BusyDialog } from './BusyDialog';

describe('BusyDialog component', () => {
  const props = {
    onClose: vi.fn(),
    title: 'Dialog Title',
    text: '49%',
    backdrop: false
  };

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders busy dialog', () => {
    const { getByText, container, asFragment } = renderWithProviders(<BusyDialog {...props}>
      <div>
        <p>child elements</p>
      </div>
    </BusyDialog>);
    getByText(props.title);
    getByText(props.text);
    getByText('child elements');
    expect(container.querySelector('.modal-backdrop')).toBeNull();
    expect(asFragment()).toMatchSnapshot();
  });

  it('renders backdrop', () => {
    const { getByText, container } = renderWithProviders(<BusyDialog
      title={props.title} onClose={props.onClose} backdrop><p>child element</p></BusyDialog>);
    getByText(props.title);
    expect(container.querySelector('.modal-backdrop')).not.toBeNull();
  });

  it('calls onClose when cancel is called', () => {
    const props = {
      onClose: vi.fn(),
      title: 'Dialog Title',
      text: '49%',
      backdrop: false
    };
    const { getByText } = renderWithProviders(<BusyDialog {...props} />);
    fireEvent.click(getByText('Cancel'));
    expect(props.onClose).toHaveBeenCalledTimes(1);
  });
});