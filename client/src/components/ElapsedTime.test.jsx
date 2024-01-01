import { renderWithProviders } from '../testHelpers';
import { ElapsedTime, elapsedTime } from './ElapsedTime';

const testCases = [
    [12, '12 seconds ago'],
    [130, '2 minutes ago'],
    [3700, '1 hour ago'],
    [3600 * 24, '24 hours ago'],
    [3600 * 25, '1 day ago'],
    [1 + 3600 * 24 * 14, '2 weeks ago'],
    [3600 * 24 * 365, '52 weeks ago'],
    [3600 * 24 * 366, '1 year ago'],
];

describe('ElapsedTime component', () => {
    beforeAll(() => {
        vi.useFakeTimers('modern');
        vi.setSystemTime(new Date('08 Feb 2023 10:12:00 GMT').getTime());
    });

    afterAll(() => vi.useRealTimers());

    it.each(testCases)('elapsedTime(%d) produces "%s"', (value, expected) => {
        const actual = elapsedTime(value * 1000);
        expect(actual).toEqual(expected);
    });

    it.each(testCases)('elapsedTime with date %d produces "%s"', (value, expected) => {
        const valueTimestamp = Date.now() - 1000 * value;
        const actual = elapsedTime(new Date(valueTimestamp));
        expect(actual).toEqual(expected);
    });

    it.each(testCases)('<ElapsedTime date={%d} /> produces "%s"', (value, expected) => {
        const { getByText } = renderWithProviders(<ElapsedTime date={value * 1000} />);
        getByText(expected);
    });

    it.each(testCases)('<ElapsedTime date={date %d} /> produces "%s"', (value, expected) => {
        const valueDate = new Date(Date.now() - 1000 * value);
        const { getByText } = renderWithProviders(<ElapsedTime date={valueDate} />);
        getByText(expected);
    });
});