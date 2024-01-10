import { render, queries, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import PropTypes from 'prop-types';
import { ReduxRouter } from '@lagunovsky/redux-react-router';
import userEvent from '@testing-library/user-event';
import { createMemoryHistory } from 'history';

import { DisplayDialog } from '../src/components/DisplayDialog';
import { createStore } from '../src/store/createStore';

import { MockBingoServer } from './MockServer';
import { bySelectorQueries, lastUpdatedQueries } from './queries';

const routerSelector = (state) => state.router

export function renderWithProviders(
  ui,
  {
    preloadedState = {},
    history = createMemoryHistory(),
    store = createStore(preloadedState),
    ...renderOptions
  } = {}
) {
  function Wrapper({ children }) {
    return (<Provider store={store}>
      <ReduxRouter history={history} routerSelector={routerSelector}>
        <DisplayDialog>
          {children}
        </DisplayDialog>
      </ReduxRouter>
    </Provider>);
  }
  Wrapper.propTypes = {
    children: PropTypes.node,
  };
  const events = userEvent.setup({
    delay: 10,
  });
  return {
    events,
    store,
    ...render(ui, {
      wrapper: Wrapper,
      queries: {
        ...queries,
        ...lastUpdatedQueries,
        ...bySelectorQueries
      },
      ...renderOptions
    })
  };
}

export function installFetchMocks(fetchMock, props) {
  return new MockBingoServer(fetchMock, props);
}

export async function setFormFields(fields, events) {
  await Promise.all(fields.map(async ({ label, value, exact }) => {
    if (exact === undefined) {
      exact = true;
    }
    const elt = await screen.findByLabelText(label, { exact });
    if (events) {
      //await events.click(elt);
      await waitFor(() => events.clear(elt));
      /*
            await waitFor(() => events.clear(elt));
        await waitFor(() => events.type(elt, value));
      }*/
    }
    await waitFor(() => fireEvent.input(elt, {
      target: {
        value
      }
    }));
  }));
  const { label, exact, value } = fields[fields.length - 1];
  const elt = await screen.findByLabelText(label, { exact });
  await waitFor(() => {
    expect(elt.value).toBe(value);
  });
}

