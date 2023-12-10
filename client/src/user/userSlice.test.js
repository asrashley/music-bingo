import fetchMock from "fetch-mock-jest";
import log from 'loglevel';

import { installFetchMocks } from '../testHelpers';
import { createStore } from '../store/createStore';
import { initialState } from '../store/initialState';
import { createGuestAccount } from './userSlice';

describe('user slice', () => {
    let apiMocks;

    beforeEach(() => {
        apiMocks = installFetchMocks(fetchMock, { loggedIn: true });
    });

    afterEach(() => {
        fetchMock.mockReset();
        log.resetLevel();
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
        log.setLevel('debug');
        await expect(dispatch(createGuestAccount('token'))).resolves.toBeDefined();
    });
})