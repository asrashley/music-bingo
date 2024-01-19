import { it } from "vitest";
import { toISOString, splitDateTime } from "./ModifyGameForm";

describe('ModifyGameForm', () => {

    it.each([
        [null, null, ""],
        ['2023-01-02', null, '2023-01-02T00:00:00Z'],
        ['2023-01-02', '12:35:56', '2023-01-02T12:35:56Z'],
        ['2023-01-02', '12:35', '2023-01-02T12:35:00Z'],
    ])('converts "%s" + "%s" to "%s"', (date, time, expected) => {
        expect(toISOString(date, time)).toEqual(expected);
    });

    it.each([
        [null, null, null],
        ['2023-01-02T12:35:56Z', '2023-01-02', '12:35'],
        ['2023-01-02T12:35:00Z', '2023-01-02', '12:35'],
    ])('splits dateTime %s', (dateTime, date, time) => {
        expect(splitDateTime(dateTime)).toEqual([date, time]);
    });
});
