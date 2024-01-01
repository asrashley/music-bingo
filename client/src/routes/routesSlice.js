import { createSlice } from '@reduxjs/toolkit';

export const initialState = {
    params: {},
    routeState: null,
    lastUpdated: 0,
};

export const routesSlice = createSlice({
    name: 'routes',
    initialState,
    reducers: {
        onRouteParamsChanged: (state, action) => {
            const { params, routeState } = action.payload;
            state.lastUpdated = Date.now();
            state.params = params;
            state.routeState = routeState;
        },
    },
});

export const { onRouteParamsChanged } = routesSlice.actions;

export default routesSlice.reducer;

