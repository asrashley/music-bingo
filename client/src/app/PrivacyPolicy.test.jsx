import React from 'react';

import { renderWithProviders } from '../../tests';
import PrivacyPolicy from './PrivacyPolicy';

describe('PrivacyPolicy component', () => {
	const completePolicy = {
		name: {
			"help": "Company Name",
			"name": "name",
			"title": "Name",
			"value": "Acme Widgets",
			"type": "text"
		},
		email: {
			"help": "Company Email",
			"name": "email",
			"title": "Email",
			"value": "acme@unit.test",
			"type": "text"
		},
		address: {
			"help": "Company Address",
			"name": "address",
			"title": "Address",
			"value": "One Simple Test",
			"type": "text"
		},
		data_center: {
			"help": "Data Center",
			"name": "data_center",
			"title": "Data Center",
			"value": "eu-west-1",
			"type": "text"
		},
		ico: {
			"help": "Information Commissioner URL",
			"name": "ico",
			"title": "Ico",
			"value": "https://an.ico.site",
			"type": "text"
		}
	};
	it('renders without throwing an exception', () => {
		const result = renderWithProviders(<PrivacyPolicy policy={completePolicy} />);
		result.getByText(completePolicy.name.value);
		result.getAllByText(completePolicy.email.value);
		result.getByText(completePolicy.address.value);
		result.getByText(completePolicy.data_center.value);
		result.getByText('an.ico.site');
		expect(result.queryByText(completePolicy.ico.value)).toBe(null);
		const { container } = result;
		expect(container.querySelectorAll('a.email').length).toBe(2);
	});

	it('renders without throwing an exception with no ICO', () => {
		const policy = {
			name: {
				"value": 'Acme Widgets'
			},
			email: {
				"value": 'acme@unit.test'
			},
			address: {
				"value": 'One Simple Test'
			},
			data_center: {
				"value": 'eu-west-1'
			}
		};
		renderWithProviders(<PrivacyPolicy policy={policy} />);
	});

	it('matches JSON snapshot', () => {
		const { asFragment } = renderWithProviders(<PrivacyPolicy policy={completePolicy} />);
		expect(asFragment()).toMatchSnapshot();
	});
});