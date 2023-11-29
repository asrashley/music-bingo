import { renderWithProviders } from '../testHelpers';
import { Input } from './Input';

describe('Input component', () => {
    const formState = {
        isDirty: false,
        dirtyFields: {},
        errors: {},
        touchedFields: {},
    };
    it('matches snapshot', () => {
        const props = {
            className: 'input-class-name',
            groupClassName: 'group-class-name',
            hint: 'hint text',
            label: 'Input Label Text',
            name: 'snapshotTest',
            type: 'text',
            formState,
            placeholder: 'Placeholder text',
            register: () => ({}),
            required: true,
        };
        const { asFragment, getByText } = renderWithProviders(<Input {...props} />);
        getByText(props.label);
        getByText(props.hint);
        expect(asFragment()).toMatchSnapshot();
    });

    it.each(['checkbox', 'date', 'text', 'time', 'number', 'password'])('creates a %s input', (type) => {
        const props = {
            label: 'Input Label',
            name: `${type}Test`,
            placeholder: `Placeholder text for ${type} field`,
            type,
            formState,
            register: () => ({}),
        };
        const { getByLabelText } = renderWithProviders(<Input {...props} />);
        const input = getByLabelText(props.label);
        expect(input.type).toEqual(type);
        expect(input.id).toEqual(`field-${props.name}`);
        expect(input.placeholder).toEqual(props.placeholder);
    });
})