import React from 'react';
import { fireEvent } from '@testing-library/react';

import { renderWithProviders } from '../testHelpers';
import { ConfirmDialog } from './ConfirmDialog';

describe('ConfirmDialog component', () => {
	it('calls onCancel() and onConfirm() when buttons are clicked', async () => {
		let cancelled = false;
		let confirmed = false;
		const props = {
			changes: [
				'change one',
				'change two'
			],
			onConfirm: () => { confirmed = true; },
			onCancel: () => { cancelled = true; },
			title: 'ConfirmDialog test',
			backdrop: false
		};

		const result = renderWithProviders(
			<ConfirmDialog {...props} />);
		result.getByText(props.title);
		props.changes.forEach(txt => result.getByText(txt));
		fireEvent.click(result.getByRole('button', { name: /Cancel/ }));
		expect(cancelled).toBe(true);
		expect(confirmed).toBe(false);
		cancelled = false;
		fireEvent.click(result.getByRole('button', { name: /Confirm/ }));
		expect(confirmed).toBe(true);
		expect(cancelled).toBe(false);
	});

	it('title is optional', () => {
		const props = {
			changes: [
			],
			onConfirm: () => false,
			onCancel: () => false
		};
		const result = renderWithProviders(
			<ConfirmDialog {...props} />);
		result.getByText("Confirm save changes");
	});

	it('matches JSON snapshot', () => {
		const props = {
			changes: [
				'change one',
				'change two'
			],
			onConfirm: () => false,
			onCancel: () => false,
			title: 'ConfirmDialog snapshot test',
			backdrop: false
		};
		const { asFragment } = renderWithProviders(
			<ConfirmDialog {...props} />);
		expect(asFragment()).toMatchSnapshot();
	});
});