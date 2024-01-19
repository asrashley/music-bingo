import fetchMockHandlerTest from 'fetch-mock/esm/client';
import jestify from 'fetch-mock-jest/jestify';
import { MockResponse } from './MockResponse';

export const fetchMock = jestify(fetchMockHandlerTest);

Object.assign(fetchMock.config, {
    fallbackToNetwork: false,
    warnOnFallback: true,
    Response: MockResponse,
});
