import React from 'react';
import { fireEvent } from '@testing-library/react';

import { renderWithProviders } from '../../testHelpers';
import { LogoutDialog } from './LogoutDialog';

describe('LogoutDialog component', () => {
	it('calls onCancel() and onConfirm() when buttons are clicked', async () => {
		const props = {
			onCancel: vi.fn(),
			onConfirm: vi.fn(),
			backdrop: false
		};

		const result = renderWithProviders(
			<LogoutDialog {...props} />);
		result.getByText('Logout from Musical Bingo?');
		fireEvent.click(result.getByText('Yes, log out'));
		expect(props.onConfirm).toHaveBeenCalledTimes(1);
		expect(props.onCancel).toHaveBeenCalledTimes(0);
		fireEvent.click(result.getByText('No, I want to stay!'));
		expect(props.onConfirm).toHaveBeenCalledTimes(1);
		expect(props.onCancel).toHaveBeenCalledTimes(1);
		expect(result.asFragment()).toMatchSnapshot();
	});
});