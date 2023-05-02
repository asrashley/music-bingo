import React from 'react';

import { renderWithProviders } from '../testHelpers';
import App from './App';


it('App component renders without throwing an exception', () => {
  renderWithProviders(<App />);
});