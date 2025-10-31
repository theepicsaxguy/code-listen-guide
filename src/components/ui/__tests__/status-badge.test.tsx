import React from 'react';
import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import { StatusBadge } from '../../../pages/Dashboard/components/StatusBadge';

describe('StatusBadge', () => {
  it('renders danger status state', () => {
    const markup = renderToStaticMarkup(<StatusBadge status="failed" />);
    expect(markup).toMatchSnapshot();
  });
});
