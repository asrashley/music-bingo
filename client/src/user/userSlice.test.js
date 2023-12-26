import fetchMock from "fetch-mock-jest";
import log from 'loglevel';

import { installFetchMocks } from '../testHelpers';
import { createStore } from '../store/createStore';
import { initialState } from '../store/initialState';
import { createGuestAccount, userSlice } from './userSlice';

describe('user slice', () => {
    let apiMocks;

    beforeEach(() => {
        apiMocks = installFetchMocks(fetchMock, { loggedIn: true });
    });

    afterEach(() => {
        fetchMock.mockReset();
        log.resetLevel();
    });

    it('failedLoginUser', () => {
        const store = createStore(initialState);
        const { dispatch, getState } = store;
        dispatch(userSlice.actions.failedLoginUser({
            body: {
                username: 'a.user@unit.test',
            },
            status: 401,
            error: 'an error',
            timestamp: 789,
        }));
        expect(getState().user).toMatchObject({
            error: 'Email address or password is incorrect',
            lastUpdated: 789,
        });
        dispatch(userSlice.actions.failedLoginUser({
            body: {
                username: 'a.username',
            },
            status: 401,
            error: 'an error',
            timestamp: 6789,
        }));
        expect(getState().user).toMatchObject({
            error: 'Username or password is incorrect',
            lastUpdated: 6789,
        });
        dispatch(userSlice.actions.failedLoginUser({
            body: {
                username: 'a.username',
            },
            status: 500,
            error: 'server error',
            timestamp: 56789,
        }));
        expect(getState().user).toMatchObject({
            error: 'server error',
            lastUpdated: 56789,
        });
    });

    it('receive guest user', () => {
        const store = createStore({
            ...initialState,
            user: {
                ...initialState.user,
                guest: {
                    username: 'a.guest',
                },
                registering: true,
                isFetching: true,
            },
        });
        const { dispatch, getState } = store;
        dispatch(userSlice.actions.receiveUser({
            payload: {
                username: 'a.guest',
                groups: ['guests'],
                accessToken: 'a.access.token',
                refreshToken: 'r.refresh.token',
            },
            timestamp: 0x123,
        }));
        expect(getState().user).toMatchObject({
            username: 'a.guest',
            groups: {
                'guests': true,
            },
            guest: {
                loggedIn: true,
            },
            lastUpdated: 0x123,
            accessToken: 'a.access.token',
            refreshToken: 'r.refresh.token',
        });
        expect(localStorage.getItem('accessToken')).toEqual('a.access.token');
        expect(localStorage.getItem('refreshToken')).toEqual('r.refresh.token');
    });

    it('registers a guest account', async () => {
        const username = 'a.guest';
        const password = 'guest-pwd';
        const email = 'a.different@email.net';
        fetchMock.put('/api/user/guest', async (url, opts) => {
            return apiMocks.jsonResponse({
                pk: 1000,
                email,
                username,
                password,
                last_login: "",
                groups: ["guests"],
                options: {
                    colourScheme: "cyan",
                    colourSchemes: ["blue", "christmas", "cyan"],
                    maxTickets: 2,
                    rows: 3,
                    columns: 5
                },
                accessToken: "access.token",
                refreshToken: "refresh.token",
            });
        });
        apiMocks.addUser({
            email,
            username,
            password,
            groups: ["guests"]
        });
        const store = createStore(initialState);
        const { dispatch } = store;
        apiMocks.logout();
        await expect(dispatch(createGuestAccount('token'))).resolves.toBeDefined();
    });

    it('failedFetchUser when user logged in', () => {
        const store = createStore({
            ...initialState,
            user: {
                ...initialState.user,
                pk: 5,
                error: 'initial error',
                accessToken: 'hhhh',
                registering: true,
                isFetching: true,
                didInvalidate: false,
            },
        });
        const { getState, dispatch } = store;
        dispatch(userSlice.actions.failedFetchUser({
            error: 'failed fetch user',
            timestamp: 5555,
        }));
        expect(getState().user).toMatchObject({
            isFetching: false,
            registering: false,
            lastUpdated: 5555,
            error: 'failed fetch user',
            didInvalidate: true,
        });
    });

    it('failedFetchToken when user not logged in', () => {
        const store = createStore({
            ...initialState,
            user: {
                ...initialState.user,
                error: 'initial error',
                accessToken: 'hhhh',
                tokenFetching: true,
                isFetching: true,
            }
        });
        const { getState, dispatch } = store;

        expect(getState().user.pk).toBeLessThan(1);
        dispatch(userSlice.actions.failedFetchToken({
            error: 'fetch token error',
            timestamp: 111,
        }));
        expect(getState().user).toMatchObject({
            tokenFetching: false,
            error: 'initial error',
            lastUpdated: 111,
            accessToken: null,
            isFetching: false,
        });
    });

    it('failedFetchToken when user is logged in', () => {
        const store = createStore({
            ...initialState,
            user: {
                ...initialState.user,
                pk: 5,
                error: 'initial error',
                accessToken: 'hhhh',
                tokenFetching: true,
                isFetching: true,
            }
        });
        const { getState, dispatch } = store;
        dispatch(userSlice.actions.failedFetchToken({
            error: 'fetch token error',
            timestamp: 222,
        }));
        expect(getState().user).toMatchObject({
            tokenFetching: false,
            error: 'fetch token error',
            lastUpdated: 222,
            accessToken: null,
            isFetching: false,
        });
    });

    it('requestCreateGuestToken', () => {
        const store = createStore(initialState);
        const { getState, dispatch } = store;
        expect(getState().user.isFetching).toEqual(false);
        dispatch(userSlice.actions.requestCreateGuestToken());
        expect(getState().user.isFetching).toEqual(true);
    });

    it('failedCreateGuestAccount', () => {
        const store = createStore(initialState);
        const { getState, dispatch } = store;
        dispatch(userSlice.actions.failedCreateGuestAccount({
            error: 'failedCreateGuestAccount error',
            timestamp: 5678,
        }));
        const { guest, lastUpdated } = getState().user;
        expect(guest.error).toEqual('failedCreateGuestAccount error');
        expect(lastUpdated).toEqual(5678);
    });

    it('failedCreateGuestToken', () => {
        const store = createStore(initialState);
        const { getState, dispatch } = store;
        dispatch(userSlice.actions.failedCreateGuestToken({
            error: 'failedCreateGuestToken error',
            timestamp: 5678,
        }));
        const { error, lastUpdated } = getState().user;
        expect(error).toEqual('failedCreateGuestToken error');
        expect(lastUpdated).toEqual(5678);
    });

    it('clearGuestDetails', () => {
        localStorage.setItem("guestUsername", "a.guest.name");
        localStorage.setItem("guestPassword", "12345");
        const store = createStore(initialState);
        store.dispatch(userSlice.actions.clearGuestDetails());
        expect(localStorage.getItem("guestUsername")).toBeNull();
        expect(localStorage.getItem("guestPassword")).toBeNull();

    });
});