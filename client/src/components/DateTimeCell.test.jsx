
import { renderWithProviders } from '../../tests';
import { DateTime } from './DateTime';
import { DateTimeCell } from './DateTimeCell';

describe('DateTimeCell component', () => {
    const dataKey = 'lastUpdate';
    const rowData = {
        id: 'id',
        lastUpdate: new Date('2023-11-27T01:23'),
    };
    it('className is optional', () => {
        const expected = DateTime({ date: rowData.lastUpdate });
        const { getByText } = renderWithProviders(<DateTimeCell rowData={rowData} dataKey={dataKey} />);
        getByText(expected);
        const errMsg = document.querySelector('span');
        expect(errMsg.className).toBe('');
    });

    it('className can be a string', () => {
        renderWithProviders(<DateTimeCell className='classname' rowData={rowData} dataKey={dataKey} />);
        const errMsg = document.querySelector('span');
        expect(errMsg.className).toBe('classname');
    });

    it('className can be a function', () => {
        const className = () => 'func-class';
        renderWithProviders(<DateTimeCell rowData={rowData} dataKey={dataKey} className={className} />);
        const errMsg = document.querySelector('span');
        expect(errMsg.className).toBe('func-class');
    });
});