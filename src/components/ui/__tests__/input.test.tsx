import React from 'react';
import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import { Input } from '../input';

describe('Input', () => {
  it('renders tokenized input', () => {
    const markup = renderToStaticMarkup(<Input placeholder="Email" />);
    expect(markup).toMatchSnapshot();
  });
});
