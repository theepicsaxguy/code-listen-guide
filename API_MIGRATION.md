# API Migration Guide

This document tracks the migration from manual API client to auto-generated Orval hooks.

## Status

✅ **API Generation Complete** - Orval successfully generated TypeScript client and React Query hooks from FastAPI OpenAPI schema.

## Generated Files

All generated files are in `src/lib/api/generated/`:
- `auth/auth.ts` - Authentication hooks
- `jobs/jobs.ts` - Job management hooks
- `outlines/outlines.ts` - Outline generation hooks
- `payments/payments.ts` - Payment processing hooks
- `player/player.ts` - Audiobook player hooks
- `admin/admin.ts` - Admin panel hooks
- `traces/traces.ts` - Job tracing hooks
- `parse/parse.ts` - Repository parsing hooks
- `episodes/episodes.ts` - Episode management hooks
- `default/default.ts` - Health check and root hooks
- `codebaseAudiobookAPI.schemas.ts` - All TypeScript types from Pydantic schemas
- `index.ts` - Main export file

## Key Hooks Generated

### Authentication
- `useRegisterApiV1AuthRegisterPost()` - User registration
- `useLoginApiV1AuthLoginPost()` - User login
- `useGetMeApiV1AuthMeGet()` - Get current user
- `usePostAuthRefresh()` - Refresh access token
- `usePostAuthLogout()` - Logout user

### Jobs
- `useCreateJobApiV1JobsPost()` - Create new job
- `useListJobsApiV1JobsGet()` - List user's jobs
- `useGetJobApiV1JobsJobIdGet()` - Get job details
- `useDeleteJobApiV1JobsJobIdDelete()` - Delete job
- `useEstimateJobCostApiV1JobsEstimatePost()` - Estimate job cost

### Outlines
- `useGetOutlineApiV1JobsJobIdOutlineGet()` - Get outline
- `useGenerateOutlineApiV1JobsJobIdOutlinePost()` - Generate outline
- `useUpdateOutlineApiV1JobsJobIdOutlinePut()` - Update outline
- `useApproveOutlineApiV1JobsJobIdOutlineApprovePost()` - Approve outline

### Payments
- `useCreatePaymentIntentPaymentsCreateIntentPost()` - Create payment intent
- `useGetPaymentHistoryPaymentsHistoryGet()` - Get payment history
- `useCreateCheckoutSessionPaymentsCreateCheckoutSessionPost()` - Create checkout session

### And many more...

## Migration Pattern

### Before (Manual API Client)
```typescript
import { apiClient } from '@/lib/api';

const job = await apiClient.createJob({
  repo_url: 'https://github.com/user/repo',
  depth_tier: 'standard',
});
```

### After (Generated Hooks)
```typescript
import { useCreateJobApiV1JobsPost } from '@/lib/api/generated';

function MyComponent() {
  const createJob = useCreateJobApiV1JobsPost();
  
  const handleCreate = async () => {
    const job = await createJob.mutateAsync({
      data: {
        repo_url: 'https://github.com/user/repo',
        depth_tier: 'standard',
      },
    });
  };
  
  return <button onClick={handleCreate}>Create</button>;
}
```

## Remaining Work

The following files still need to be updated to use generated hooks:
- All files importing from `@/lib/api` (27 files found)
- `src/contexts/AuthContext.tsx` - Needs complete rewrite to use hooks
- All page components using `apiClient.*`

## Files Requiring Updates

See: `grep -r "from '@/lib/api'" src/`

## Next Steps

1. Update `AuthContext.tsx` to use generated auth hooks
2. Update all page components to use generated hooks instead of `apiClient`
3. Remove all manual API client usage
4. Run TypeScript build to verify no errors
5. Test all endpoints work correctly

## Regeneration

After backend changes:
```bash
npm run generate:api
```

This will regenerate all hooks and types from the latest OpenAPI schema.

