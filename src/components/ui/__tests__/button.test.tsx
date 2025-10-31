import React from 'react';
import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import { Button } from '../button';

describe('Button', () => {
  it('renders primary button consistently', () => {
    const markup = renderToStaticMarkup(<Button>Primary</Button>);
    expect(markup).toMatchSnapshot();
  });
});
