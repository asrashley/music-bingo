import { within, fireEvent } from '@testing-library/react';
import { renderWithProviders } from '../../../tests';
import { PastGamesLastUsage, sortData } from './PastGamesLastUsage';

const themes = [{
    "slug": "100nows",
    "title": "100 Nows",
    "row": {
        "2020-02": 1,
        "2020-08": 1,
        "2022-04": 1,
        "2022-11": 1,
        "2023-09": 1
    },
    "lastUsed": new Date("2023-09-21T17:52:25.041Z"),
    "elapsedTime": 5795103227
}, {
    "slug": "1973",
    "title": "1973",
    "row": {
        "2023-10": 1
    },
    "lastUsed": new Date("2023-10-05T16:44:53.615Z"),
    "elapsedTime": 4589554653
}, {
    "slug": "2000s",
    "title": "2000s",
    "row": {
        "2018-08": 1,
        "2019-06": 1,
        "2020-01": 1,
        "2021-11": 1,
        "2022-08": 1,
        "2023-05": 1
    },
    "lastUsed": new Date("2023-05-18T09:49:39.188Z"),
    "elapsedTime": 16710469080
}];

describe('PastGamesLastUsage component', () => {
    beforeAll(() => {
        vi.useFakeTimers('modern');
        vi.setSystemTime(new Date('08 Feb 2023 10:12:00 GMT').getTime());
    });

    afterAll(() => vi.useRealTimers());

    it('PastGamesLastUsage matches snapshot when loaded', () => {
        const { asFragment } = renderWithProviders(
            <PastGamesLastUsage themes={themes} loading={false} />);
        expect(asFragment()).toMatchSnapshot();
    });

    it('PastGamesLastUsage matches snapshot when loading', () => {
        const { asFragment } = renderWithProviders(
            <PastGamesLastUsage themes={[]} loading={true} />);
        expect(asFragment()).toMatchSnapshot();
    });

    it.each(['title', 'lastUsed', 'elapsedTime'])('PastGamesLastUsage can sort by %s', async (column) => {
        function clickSortButton() {
            if (column === 'title') {
                fireEvent.click(getByText('Theme'));
            } else if (column === 'lastUsed') {
                fireEvent.click(getByText('Last Used'));
            } else {
                fireEvent.click(getByText('Elapsed Time'));
            }
        }
        const { getByText, getAllBySelector, findAllBySelector } = renderWithProviders(
            <PastGamesLastUsage themes={themes} loading={false} />);
        getByText('100 Nows');
        let expected = themes.map(item => item.title);
        let tableRows = getAllBySelector('.rs-table-body-row-wrapper .rs-table-row');
        tableRows.forEach((row, index) => {
            within(row).getByText(expected[index]);
        });

        let sortedThemes = sortData(themes, column, 'desc');
        expected = sortedThemes.map(item => item.title);
        clickSortButton();
        tableRows = await findAllBySelector('.rs-table-body-row-wrapper .rs-table-row');
        tableRows.forEach((row, index) => {
            within(row).getByText(expected[index]);
        });

        sortedThemes = sortData(sortedThemes, column, 'asc');
        expected = sortedThemes.map(item => item.title);
        clickSortButton();
        tableRows = await findAllBySelector('.rs-table-body-row-wrapper .rs-table-row');
        tableRows.forEach((row, index) => {
            within(row).getByText(expected[index]);
        });
    });
});