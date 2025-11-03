# API Client Regeneration Guide

## Problem
The generated API client has long function names like `useGetAgentStatsApiV1AdminAgentsStatsGet` instead of short names like `useGetAgentStats`.

## Root Cause
The API client was generated before operation IDs were added to backend routes, or the OpenAPI spec wasn't regenerated.

## Solution

### Step 1: Verify Backend Routes Have Operation IDs
All backend routes should have `operation_id` parameters. Verified routes:
- ✅ `agents_admin.py`: `listAgentJobs`, `getAgentJobDetails`, `getAgentStats`, `getJobLogs`, `retryFailedJob`
- ✅ `admin_agents_crud.py`: `listAgents`, `createAgent`, `updateAgent`, `deleteAgent`, `getAgent`, `getAgentRegistry`
- ✅ `admin_plugins.py`: `listPlugins`, `getPlugin`, `createPlugin`, `updatePlugin`, `deletePlugin`, `getToolRegistry`, `getCodeRegistryPlugins`

### Step 2: Ensure Backend Server is Running
The OpenAPI spec is generated from the running FastAPI server:
```bash
cd backend
uvicorn backend.main:app --reload
```

### Step 3: Regenerate API Client
```bash
npm run generate:api
```

This will:
1. Fetch the OpenAPI spec from `http://localhost:8000/openapi.json`
2. Generate new hooks with short names based on operation IDs:
   - `useGetAgentStats` (instead of `useGetAgentStatsApiV1AdminAgentsStatsGet`)
   - `useListAgents` (instead of `useListAgentsApiV1AdminAgentsListGet`)
   - `useGetCodeRegistryPlugins` (instead of `useGetCodeRegistryPluginsApiV1AdminToolsCodeRegistryGet`)

### Step 4: Update Frontend Code
After regeneration, update imports in:
- `src/pages/admin/AgentManagement.tsx`
- `src/pages/admin/AgentMonitoring.tsx`
- `src/pages/admin/Dashboard.tsx`
- `src/pages/admin/AuditLogs.tsx`
- `src/pages/admin/Plugins.tsx`

## Expected Names After Regeneration

### Agent Routes
- `useListAgentJobs` - List agent jobs
- `useGetAgentJobDetails` - Get job details
- `useGetAgentStats` - Get agent statistics
- `useGetJobLogs` - Get job logs
- `useRetryFailedJob` - Retry failed job

### Agent CRUD Routes
- `useListAgents` - List all agents
- `useCreateAgent` - Create agent
- `useUpdateAgent` - Update agent
- `useDeleteAgent` - Delete agent
- `useGetAgent` - Get agent details
- `useGetAgentRegistry` - Get agent registry

### Plugin Routes
- `useListPlugins` - List plugins
- `useGetPlugin` - Get plugin
- `useCreatePlugin` - Create plugin
- `useUpdatePlugin` - Update plugin
- `useDeletePlugin` - Delete plugin
- `useGetToolRegistry` - Get tool registry
- `useGetCodeRegistryPlugins` - Get code registry plugins

## Verification
After regeneration, check `src/lib/api/generated/admin/admin.ts` - all hook names should be 1-3 words and not contain "ApiV1".

