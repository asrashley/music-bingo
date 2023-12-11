import { renderWithProviders } from '../../testHelpers';

import { PastGamesButtons } from './PastGamesButtons';

describe('PastGamesButtons', () => {
    it.each(['all', 'calendar', 'popularity', 'usage'])('renders buttons for page "%s"', (page) => {
        const { container } = renderWithProviders(<PastGamesButtons page={page} />);
        expect(container.querySelector(`.page-${page}`)).not.toBeNull();
    });
})