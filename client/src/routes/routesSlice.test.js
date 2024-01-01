import { createStore } from '../store/createStore';
import { initialState } from '../store/initialState';

import { onRouteParamsChanged } from './routesSlice';

describe('routesSlice', () => {
    beforeEach(() => {
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.restoreAllMocks();
        vi.useRealTimers();
    });

    it('onRouteParamsChanged', () => {
        const store = createStore({ ...initialState });
        const params = {
            slug: 'slug',
        };
        const pathname = '/history/themes/slug';
        const hash = 'hash';
        const routeState = {
            route: 'state',
        };
        const date = new Date(2000, 1, 1, 19)
        vi.setSystemTime(date)
        store.dispatch(onRouteParamsChanged({ params, hash, pathname, routeState }));
        const { routes } = store.getState();
        expect(routes.params).toEqual(params);
        expect(routes.routeState).toEqual(routeState);
        expect(routes.lastUpdated).toEqual(949431600000);
    });
});