import React from 'react';
import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import { Badge } from '../badge';

describe('Badge', () => {
  it('renders danger badge', () => {
    const markup = renderToStaticMarkup(<Badge variant="danger">Failed</Badge>);
    expect(markup).toMatchSnapshot();
  });
});
