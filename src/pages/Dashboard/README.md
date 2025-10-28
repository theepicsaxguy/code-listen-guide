# Dashboard Architecture

This directory contains the refactored Dashboard with a clean separation of concerns following React best practices.

## Structure

```
Dashboard/
├── components/           # React components
│   ├── StatusBadge.tsx   # Status indicator component
│   ├── PlanBadge.tsx     # Subscription plan badge
│   ├── Sidebar.tsx       # Navigation sidebar
│   ├── OverviewPage.tsx  # Dashboard overview/home page
│   ├── AudiobooksPage.tsx # Audiobooks library listing
│   ├── AudiobookDetailPage.tsx # Audiobook player/detail view
│   ├── SettingsPage.tsx  # User settings page
│   ├── BillingPage.tsx   # Billing and payment history
│   └── index.ts          # Component exports
├── hooks/                # Custom React hooks
│   ├── useAudiobooks.ts  # Audiobook data fetching hooks
│   ├── useUser.ts        # User profile hooks
│   ├── useBilling.ts     # Billing/payment hooks
│   └── index.ts          # Hook exports
├── types/                # TypeScript type definitions
│   └── index.ts          # Dashboard-specific types
├── utils/                # Utility functions
│   ├── formatters.ts     # Date, time, duration formatters
│   └── index.ts          # Utility exports
└── README.md            # This file
```

## Key Features

### API Integration
- All components use real API endpoints via custom hooks
- No mock data - fully connected to backend
- Uses React Query for data fetching and caching

### Custom Hooks
- **useAudiobooks**: Fetches and manages audiobook list with filtering
- **useAudiobook**: Fetches single audiobook details
- **useAudiobookChapters**: Fetches chapter/player data
- **useCreateAudiobook**: Mutation hook for creating new audiobooks
- **useDeleteAudiobook**: Mutation hook for deleting audiobooks
- **useUser**: Fetches current user profile
- **usePaymentHistory**: Fetches billing/payment history

### Components
All components are self-contained and follow React best practices:
- Functional components with hooks
- Proper TypeScript typing
- Loading and error states
- Accessibility attributes

### Type Safety
- Uses existing types from `lib/types.ts`
- Dashboard-specific types in `Dashboard/types/`
- Full TypeScript coverage

## Usage

```tsx
import { Dashboard } from './pages/Dashboard';

// The main Dashboard component handles all routing internally
<Dashboard />
```

## API Dependencies

The dashboard connects to these API endpoints:
- `GET /auth/me` - User profile
- `GET /jobs` - List audiobooks (with filtering)
- `GET /jobs/:id` - Get single audiobook
- `POST /jobs` - Create new audiobook
- `DELETE /jobs/:id` - Delete audiobook
- `GET /player/:id` - Get player/chapter data
- `GET /payments/history` - Payment history

## Future Enhancements

1. **Analytics API**: Currently using mock data for usage charts
2. **Settings API**: Add endpoints for updating user preferences
3. **Real-time Updates**: Consider WebSocket/SSE for job progress
4. **Search**: Implement server-side search functionality
5. **Pagination**: Add pagination support for large audiobook lists
