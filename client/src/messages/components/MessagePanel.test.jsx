import React from 'react';

import { renderWithProviders } from '../../../tests';
import { MessagePanel, MessagePanelComponent } from './MessagePanel';

import { initialState } from '../../store/initialState';

describe('MessagePanel component', () => {
	const messages = [{
		id: 2,
		text: "a single line message",
		heading: "message heading",
		hidden: false,
		type: "success",
		timestamp: 1675888498892
	}, {
		id: 3,
		text: "message 2",
		heading: "message heading 2",
		hidden: false,
		type: "info",
		timestamp: 1675888498900
	}];

	beforeAll(() => {
		vi.useFakeTimers('modern');
		vi.setSystemTime(new Date('08 Feb 2023 20:34:58 GMT').getTime());
	});

	afterAll(() => vi.useRealTimers());

	it('MessagePanelComponent renders a list of messages', () => {
		const result = renderWithProviders(
			<MessagePanelComponent messages={messages} dispatch={() => false} />);
		messages.forEach((msg) => {
			result.getByText(msg.text);
			result.getByText(msg.heading);
		});
	});

	it('fetches messages from the Redux store', () => {
		const preloadedState = {
			...initialState,
			messages: {
				messages: {},
				duration: 15000,
				nextMessageId: 4,
			}
		};
		messages.forEach(msg => preloadedState.messages.messages[msg.id] = msg);
		const result = renderWithProviders(
			<MessagePanel />, { preloadedState });
		messages.forEach((msg) => {
			result.getByText(msg.text);
			result.getByText(msg.heading);
		});
	});

	it('matches JSON snapshot', () => {
		const { asFragment } = renderWithProviders(
			<MessagePanelComponent messages={messages} dispatch={() => false} />);
		expect(asFragment()).toMatchSnapshot();
	});
});