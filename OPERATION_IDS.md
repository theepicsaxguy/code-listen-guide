# Operation IDs Added

Short operation IDs have been added to key FastAPI routes. When you regenerate the API client with `npm run generate:api`, the hooks will have clean, short names:

## Auth Routes
- `useLogin()` - Login user
- `useRegister()` - Register user  
- `useLogout()` - Logout user
- `useGetMe()` - Get current user
- `useRefreshToken()` - Refresh access token

## Job Routes
- `useListJobs()` - List user's jobs
- `useCreateJob()` - Create new job
- `useGetJob()` - Get job details
- `useDeleteJob()` - Delete job
- `useEstimateCost()` - Estimate job cost
- `useStartJob()` - Start job workflow
- `useCancelJob()` - Cancel job

## Outline Routes
- `useGetOutline()` - Get outline
- `useGenerateOutline()` - Generate outline
- `useUpdateOutline()` - Update outline
- `useApproveOutline()` - Approve outline

## Player Routes
- `useGetPlayerData()` - Get audiobook player data

## Payment Routes
- `useCreatePaymentIntent()` - Create Stripe payment intent
- `useGetPaymentHistory()` - Get payment history

## Parse Routes
- `useParseRepository()` - Parse repository

## Adding More

To add operation IDs to more routes, add `operation_id="shortName"` to the route decorator:

```python
@router.get("/some-endpoint", operation_id="getSomething")
async def get_something():
    ...
```

Then regenerate: `npm run generate:api`

