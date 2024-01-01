//import { afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import 'vitest-dom/extend-expect';
import createFetchMock from 'vitest-fetch-mock';
import { vi } from 'vitest';

const fetchMocker = createFetchMock(vi);

// sets globalThis.fetch and globalThis.fetchMock to our mocked version
fetchMocker.enableMocks();

globalThis.jest = vi;

/* multipart-stream library requires TextEncoder and TextDecoder
 * that are not part of jsdom */
if (typeof global.TextEncoder === 'undefined') {
    const { TextEncoder } = require('util');
    global.TextEncoder = TextEncoder;
}
if (typeof global.TextDecoder === 'undefined') {
    const { TextDecoder } = require('util');
    global.TextDecoder = TextDecoder;
}

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

global.__BUILD_INFO__ = {
    branch: "main",
    buildDate: "2023-02-14T09:52:40.655Z",
    commit: {
        "hash": "914af0ce5972379b108d54f78e3162fdbb8551a1",
        "shortHash": "914af0c"
    },
    tags: "v0.2.4",
    version: "0.2.5",
};

// runs a cleanup after each test case (e.g. clearing jsdom)
afterEach(() => {
    cleanup();
});