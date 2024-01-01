import { renderWithProviders } from "../testHelpers";
import { LinkCell } from "./LinkCell";


describe('LinkCell component', () => {
    const data = {
        pk: 5,
        duration: 30016,
        album: "The 50s 60 Classic Fifties Hits",
        filename: "01 Rock Around The Clock.mp3",
        title: "Rock Around The Clock",
        artist: "Bill Haley & His Comets"
    };

    const makeLink = (rowData) => `/song/${rowData.pk}`;

    it('matches snapshot', () => {
        const { asFragment } = renderWithProviders(
            <LinkCell rowData={data} dataKey="pk" to={makeLink} className="link-class" />);
        expect(asFragment()).toMatchSnapshot();
    });

    it('className can be a function', () => {
        const classNameFn = () => 'link-func-class';
        const { getBySelector } = renderWithProviders(
            <LinkCell rowData={data} dataKey="pk" to={makeLink} className={classNameFn} />);
        getBySelector('.link-func-class');
    });

    it('allows rowData to be null', () => {
        renderWithProviders(<LinkCell dataKey="pk" to={makeLink} />);
    });
});