import { createStore } from '../store/createStore';
import { initialState } from '../store/initialState'
import { fetchSystemIfNeeded, initialGitInfo } from './systemSlice';

describe('systemSlice', () => {
  beforeAll(() => {
    jest.useFakeTimers('modern');
    jest.setSystemTime(new Date('04 Dec 2022 03:12:00 GMT').getTime());
  });

  afterAll(() => jest.useRealTimers());

  it('fetches git information from a DOM element', async () => {
    const gitInfo = {
      "branch": "client-tests",
      "buildDate": "2023-02-14T09:52:40.655Z",
      "commit": {
        "hash": "914af0ce5972379b108d54f78e3162fdbb8551a1",
        "shortHash": "914af0c"
      },
      "tags": "v0.2.0"
    };
    document.body.innerHTML =
      '<div id="root">' +
      '</div>' +
      '<script type="application/json" id="buildInfo">' +
      JSON.stringify(gitInfo) +
      '</script>';
    const store = createStore(initialState, true);
    expect(store.getState().system.gitInfo).toStrictEqual(initialGitInfo);
    await store.dispatch(fetchSystemIfNeeded());
    expect(store.getState().system.gitInfo).toStrictEqual(gitInfo);
  });

  it('produces an error if the git info DOM element is missing', async () => {
    document.body.innerHTML = '<div id="root"></div>';
    const expected = {
      ...initialState.system,
      error: "Failed to find build information DOM element",
      lastUpdated: Date.now()
    };
    const store = createStore(initialState);
    expect(store.getState().system.gitInfo).toStrictEqual(initialGitInfo);
    await store.dispatch(fetchSystemIfNeeded());
    expect(store.getState().system).toStrictEqual(expected);
  });

  it('produces an error if the git info DOM element has invalid JSON', async () => {
    document.body.innerHTML = '<div id="root"></div>' +
      '<script type="application/json" id="buildInfo" > ' +
      'invalid json' +
      '</script>';
    const expected = {
      ...initialState.system,
      lastUpdated: Date.now()
    };
    const store = createStore(initialState);
    expect(store.getState().system.gitInfo).toStrictEqual(initialGitInfo);
    await store.dispatch(fetchSystemIfNeeded());
    const state = store.getState().system;
    expect(state.error).not.toBeNull();
    expect(state.error).toMatch(/SyntaxError/i);
    expected.error = state.error;
    expect(store.getState().system).toStrictEqual(expected);
  });
});