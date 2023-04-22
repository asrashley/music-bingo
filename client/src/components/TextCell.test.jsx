
import { renderWithProviders } from '../testHelpers';
import { TextCell } from './TextCell';

describe('ErrorMessage component', () => {
  it('className is optional', () => {
    const dataKey = 'title';
    const rowData = {
      id: 'id',
      title: 'A Title'
    };
    const { getByText } = renderWithProviders(<TextCell rowData={rowData} dataKey={dataKey} />);
    getByText(rowData.title);
    const errMsg = document.querySelector('span');
    expect(errMsg.className).toBe('');
  });

  it('className can be a string', () => {
    const dataKey = 'title';
    const rowData = {
      id: 'id',
      title: 'A Title'
    };
    renderWithProviders(<TextCell className='classname' rowData={rowData} dataKey={dataKey} />);
    const errMsg = document.querySelector('span');
    expect(errMsg.className).toBe('classname');
  });

  it('className can be a function', () => {
    const dataKey = 'title';
    const rowData = {
      id: 'id',
      title: 'A Title'
    };
    const className = () => 'func-class';
    renderWithProviders(<TextCell rowData={rowData} dataKey={dataKey} className={className} />);
    const errMsg = document.querySelector('span');
    expect(errMsg.className).toBe('func-class');
  });
});