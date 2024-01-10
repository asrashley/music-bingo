import { renderWithProviders } from "../../tests";

import { ElapsedTimeCell } from './ElapsedTimeCell';

describe('ElapsedTimeCell component', () => {
    const data = {
        pk: 5,
        duration: 30016,
        album: "The 50s 60 Classic Fifties Hits",
        filename: "01 Rock Around The Clock.mp3",
        title: "Rock Around The Clock",
        artist: "Bill Haley & His Comets"
    };

    it('matches snapshot', () => {
        const { asFragment } = renderWithProviders(
            <ElapsedTimeCell dataKey="pk" rowData={data} className="class-name" />);
        expect(asFragment()).toMatchSnapshot();
    });

    it('className can be a function', () => {
        const classNameFn = () => 'link-func-class';
        const { getBySelector } = renderWithProviders(
            <ElapsedTimeCell rowData={data} dataKey="pk" className={classNameFn} />);
        getBySelector('.link-func-class');
    });

    it('allows rowData to be null', () => {
        renderWithProviders(<ElapsedTimeCell dataKey="pk" />);
    });
});