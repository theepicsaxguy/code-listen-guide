import React from 'react';
import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import { Card, CardContent, CardHeader, CardTitle } from '../card';

describe('Card', () => {
  it('renders surface card', () => {
    const markup = renderToStaticMarkup(
      <Card>
        <CardHeader>
          <CardTitle>Sample</CardTitle>
        </CardHeader>
        <CardContent>Body</CardContent>
      </Card>,
    );
    expect(markup).toMatchSnapshot();
  });
});
