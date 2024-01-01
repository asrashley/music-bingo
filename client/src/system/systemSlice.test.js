import { createStore } from '../store/createStore';
import { initialState } from '../store/initialState'
import { fetchSystemIfNeeded, initialBuildInfo } from './systemSlice';

describe('systemSlice', () => {
  it('fetches git information from __BUILD_INFO__', async () => {
    const store = createStore(initialState, true);
    expect(store.getState().system.buildInfo).toStrictEqual(initialBuildInfo);
    await store.dispatch(fetchSystemIfNeeded());
    expect(store.getState().system.buildInfo).toStrictEqual(globalThis.__BUILD_INFO__);
  });
});