import { DateTime } from './DateTime';

describe('DateTime conversion function', () => {
  beforeAll(() => {
    vi.useFakeTimers('modern');
    vi.setSystemTime(new Date('04 Dec 2022 03:12:00 GMT').getTime());
  });

  afterAll(() => vi.useRealTimers());

  const testCases = [
    ['UTC number with timezone', 1675455186677, { useUTC: true, withTimezone: true }, '20:13:06 03/02/2023 UTC'],
    ['UTC number no timezone', 1675455186677, { useUTC: true, withTimezone: false }, '20:13:06 03/02/2023'],
    ['date with timezone', new Date(1675455186677), { useUTC: true, withTimezone: true }, '20:13:06 03/02/2023 UTC'],
    ['date no timezone', new Date(1675455186677), { useUTC: true, withTimezone: false }, '20:13:06 03/02/2023'],
    ['UTC isodatetime with timezone', '2023-02-03T20:13:06Z', { useUTC: true, withTimezone: true }, '20:13:06 03/02/2023 UTC'],
    ['isodatetime no date', '2023-02-03T20:13:06Z', { useUTC: true, withTimezone: false, withTime: false }, '03/02/2023'],
    ['isodatetime no date should not have timezone', '2023-02-03T20:13:06Z', { useUTC: true, withTimezone: true, withTime: false }, '03/02/2023'],
    ['isodatetime no time', '2023-02-03T20:13:06Z', { useUTC: true, withTimezone: true, withDate: false }, '20:13:06 UTC'],
    ['isodatetime no time', '2023-02-03T20:13:06Z', { useUTC: true, withTimezone: false, withDate: false }, '20:13:06'],
    ['12 hour clock', '2023-02-03T20:13:06Z', { useUTC: true, withTimezone: false, ampm: true, withDate: false }, '8:13:06 pm'],
    ['12 hour clock', '2023-02-03T06:13:06Z', { useUTC: true, withTimezone: false, ampm: true, withDate: false }, '6:13:06 am'],
    ['12 hour clock', '2023-02-03T12:13:06Z', { useUTC: true, withTimezone: false, ampm: true, withDate: false }, '12:13:06 pm'],
  ];
  it.each(testCases)('%s', (title, date, params, expected) => {
    const result = DateTime({ date, ...params });
    expect(result).toBe(expected);
  });
});
