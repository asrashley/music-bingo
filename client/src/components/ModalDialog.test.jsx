import React from 'react';
import { fireEvent, screen } from '@testing-library/react'

import { renderWithProviders, createJsonWithProviders } from '../testHelpers';
import { ModalDialog } from './ModalDialog';

describe('ModalDialog component', () => {
	it('calls onCancel() when close button is clicked', () => {
		let cancelled = false;
		const onCancel = () => { cancelled = true; };
		const result = renderWithProviders(
			<ModalDialog title="ModalDialog Test" onCancel={onCancel} />);
		result.getByText("ModalDialog Test");
		expect(result.getByRole('document').id).toBe('dialogbox');
		fireEvent.click(screen.getByRole('button', { label: "Close" }));
		expect(cancelled).toBe(true);
	});

	it('the id can be modified', () => {
		const onCancel = () => false;
		const result = renderWithProviders(
			<ModalDialog title="ModalDialog Test" id="testid" onCancel={onCancel} />);
		result.getByText("ModalDialog Test");
		expect(result.getByRole('document').id).toBe('testid');
	});

	it('children rendered', () => {
		const onCancel = () => false;
		const result = renderWithProviders(
			<ModalDialog title="ModalDialog Test" onCancel={onCancel}>
				<div><p>This is the dialog body</p></div>
			</ModalDialog>);
		result.getByText("This is the dialog body");
	});

	it('footer is rendered', () => {
		const onCancel = () => false;
		const footer = (<div><p>This is a footer</p></div>);
		const result = renderWithProviders(
			<ModalDialog title="ModalDialog Test" footer={footer} onCancel={onCancel} />);
		result.getByText("This is a footer");
	});

	it('matches JSON snapshot', () => {
		const onCancel = () => false;
		const footer = (<div><p>This is the dialog footer</p></div>);
		const { tree } = createJsonWithProviders(
			<ModalDialog title="ModalDialog Test" onCancel={onCancel} footer={footer}>
				<div><p>This is the dialog body</p></div>
			</ModalDialog>);
		expect(tree).toMatchSnapshot();
	});
});