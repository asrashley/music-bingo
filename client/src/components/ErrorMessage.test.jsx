
import { renderWithProviders } from '../../tests';
import { ErrorMessage } from './ErrorMessage';

describe('ErrorMessage component', () => {
  it('returns null if there is no error', () => {
    renderWithProviders(<ErrorMessage error={null} />);
    const errMsg = document.querySelector('.error-message');
    expect(errMsg).toBe(null);
  });

  it('shows error message', () => {
    const error = 'an error message';
    const result = renderWithProviders(<ErrorMessage error={error} />);
    result.getByText(error);
  });
});