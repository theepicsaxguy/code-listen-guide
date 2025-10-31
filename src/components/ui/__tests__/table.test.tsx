import React from 'react';
import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../table';

describe('Table', () => {
  it('renders tokenized table shell', () => {
    const markup = renderToStaticMarkup(
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Header</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell>Value</TableCell>
          </TableRow>
        </TableBody>
      </Table>,
    );
    expect(markup).toMatchSnapshot();
  });
});
