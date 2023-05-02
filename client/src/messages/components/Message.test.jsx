import React from 'react';
import { fireEvent, screen } from '@testing-library/react';

import { renderWithProviders } from '../../testHelpers';
import { Message } from './Message';

describe('Message component', () => {
	it('calls clearMessage() when close button is clicked', () => {
		const msg = {
			id: 1,
			text: "a single line message",
			heading: "message heading",
			hidden: false,
			type: "success",
			timestamp: 1675888498892
		};
		let cleared = false;
		const result = renderWithProviders(
			<Message msg={msg} clearMessage={() => { cleared = true; }} />);
		result.getByText(msg.text);
		result.getByText(msg.heading);
		fireEvent.click(screen.getByRole('button', { label: "Close" }));
		expect(cleared).toBe(true);
	});

	it('matches JSON snapshot', () => {
		const msg = {
			id: 2,
			text: [
				"line 1 of message",
				"line 2 of message"
			],
			heading: "message heading",
			hidden: false,
			type: "info",
			timestamp: 1675888498892
		};
		const { asFragment } = renderWithProviders(
			<Message msg={msg} clearMessage={() => false} />);
		expect(asFragment()).toMatchSnapshot();
	});
});