import fetchMockHandlerTest from 'fetch-mock/esm/client';
import jestify from 'fetch-mock-jest/jestify';

export const fetchMock = jestify(fetchMockHandlerTest);
