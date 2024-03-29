import React from 'react';
import { fireEvent, screen } from '@testing-library/react';

import { renderWithProviders } from '../../tests';
import { ProgressDialog } from './ProgressDialog';

describe('ProgressDialog component', () => {
	it('calls onCancel() when any close button is clicked', async () => {
		const props = {
			progress: {
				added: [{
					'count': 5,
					'name': 'songs'
				}],
				errors: [],
				text: '25%',
				pct: 25.0,
				phase: 1,
				numPhases: 1,
				timestamp: 124
			},
			onCancel: () => { cancelled = true; },
			onClose: () => { cancelled = true; },
			title: 'ProgressDialog test'
		};
		let cancelled = false;
		const result = renderWithProviders(
			<ProgressDialog {...props} />);
		result.getByText(props.title);
		result.getByText('5 songs');
		const matches = await result.findAllByText(props.progress.text);
		expect(matches.length).toBe(2);
		expect(screen.queryAllByText('Close').length).toBe(0);
		const buttons = screen.getAllByRole('button', { label: "Cancel" });
		expect(buttons.length).toBe(2);
		buttons.forEach((btn) => {
			cancelled = false;
			fireEvent.click(btn);
			expect(cancelled).toBe(true);
		});
	});

	it('shows close button when done', async () => {
		const props = {
			progress: {
				added: [{
					'count': 5,
					'name': 'songs'
				}],
				errors: [],
				text: '100%',
				pct: 100.0,
				phase: 1,
				done: true,
				numPhases: 1,
				timestamp: 124
			},
			onCancel: () => { cancelled = true; },
			onClose: () => { cancelled = true; },
			title: 'ProgressDialog test'
		};
		let cancelled = false;
		const result = renderWithProviders(
			<ProgressDialog {...props} />);
		result.getByText(props.title);
		result.getByText('5 songs');
		const matches = await result.findAllByText(props.progress.text);
		expect(matches.length).toBe(2);
		fireEvent.click(screen.getByText('Close'));
		expect(cancelled).toBe(true);
	});

	it('matches JSON snapshot', () => {
		const props = {
			progress: {
				added: [{
					'count': 5,
					'name': 'songs'
				}, {
					'count': 10,
					'name': 'tracks'
				}],
				done: false,
				errors: [],
				text: '35%',
				pct: 35.0,
				phase: 1,
				numPhases: 1,
				timestamp: 124
			},
			onCancel: () => false,
			onClose: () => false,
			title: 'ProgressDialog snapshot'
		};
		const { asFragment } = renderWithProviders(
			<ProgressDialog {...props} />);
		expect(asFragment()).toMatchSnapshot();
	});
});