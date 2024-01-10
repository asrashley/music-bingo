import { Route, Routes, Outlet } from 'react-router-dom';
import { createMemoryHistory } from 'history';
import { waitFor } from '@testing-library/react';

import { renderWithProviders } from '../../../tests';

import { RouteParams } from './RouteParams';

import { createStore } from '../../store/createStore';
import { initialState } from '../../store/initialState';

function IndexPage() {
    return <div className="index-page">Hello World</div>;
}

function DirectoryListPage() {
    return <div className="DirectoryListPage"></div>;
}

describe('RouteParams component', () => {
    it('sets empty params', () => {
        const store = createStore(initialState);

        renderWithProviders(<Routes>
            <Route path="/" element={<><RouteParams /><IndexPage /></>} />
        </Routes>, { store });
        const { routes } = store.getState();
        expect(routes.params).toEqual({});
    });

    it('updates parameters', async () => {
        const history = createMemoryHistory({
            initialEntries: ['/'],
            initialIndex: 0,
        });
        const store = createStore(initialState);
        renderWithProviders(<Routes>
            <Route path="/" element={<><RouteParams /><IndexPage /></>} />
            <Route path="clips" element={<><RouteParams /><Outlet /></>}>
                <Route path="" element={<DirectoryListPage />} />
                <Route path=":dirPk" element={<DirectoryListPage />} />
            </Route>
        </Routes>, { history, store });
        expect(store.getState().routes.params).toEqual({});
        await waitFor(() => {
            history.push('/clips/now');
        });
        expect(store.getState().routes.params).toEqual({
            dirPk: 'now',
        });
    });
});