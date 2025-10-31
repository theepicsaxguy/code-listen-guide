import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { AdminLayout } from "@/components/admin/AdminLayout";
import Index from "./pages/Index";
import Auth from "./pages/Auth";
import Dashboard from "./pages/Dashboard";
import Submit from "./pages/Submit";
import JobDetails from "./pages/JobDetails";
import OutlinePreview from "./pages/OutlinePreview";
import Player from "./pages/Player";
import NotFound from "./pages/NotFound";
import WhyWeExist from "./pages/WhyWeExist";
import AdminLogin from "./pages/admin/Login";
import AdminDashboard from "./pages/admin/Dashboard";
import AdminUsers from "./pages/admin/Users";
import AdminPayments from "./pages/admin/Payments";
import AdminContent from "./pages/admin/Content";
import ContentVersioning from "./pages/admin/ContentVersioning";
import AgentMonitoring from "./pages/admin/AgentMonitoring";
import JobTracing from "./pages/admin/JobTracing";
import Support from "./pages/admin/Support";
import AdminAuditLogs from "./pages/admin/AuditLogs";
import AdminSettings from "./pages/admin/Settings";
import ChonkieTest from "./pages/admin/ChonkieTest";
import AgentTest from "./pages/admin/AgentTest";
import AdminParse from "./pages/AdminParse";
import WorkflowList from "./pages/admin/workflows/WorkflowList";
import WorkflowDetails from "./pages/admin/workflows/WorkflowDetails";
import AdminPlugins from "./pages/admin/Plugins";
import AgentManagement from "./pages/admin/AgentManagement";

const queryClient = new QueryClient();

const App = () => (
  <ErrorBoundary>
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
        <AuthProvider>
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="/why-we-exist" element={<WhyWeExist />} />
              <Route path="/auth" element={<Auth />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/submit" element={<Submit />} />
              <Route path="/jobs/:jobId" element={<JobDetails />} />
              <Route path="/jobs/:jobId/outline" element={<OutlinePreview />} />
              <Route path="/player/:jobId" element={<Player />} />
              <Route path="/admin/login" element={<AdminLogin />} />
              <Route path="/admin" element={<AdminLayout />}>
                <Route index element={<AdminDashboard />} />
                <Route path="users" element={<AdminUsers />} />
                <Route path="payments" element={<AdminPayments />} />
                <Route path="content" element={<AdminContent />} />
                <Route path="versioning" element={<ContentVersioning />} />
                <Route path="agents" element={<AgentMonitoring />} />
                <Route path="agents/manage" element={<AgentManagement />} />
                <Route path="plugins" element={<AdminPlugins />} />
                <Route path="tracing" element={<JobTracing />} />
                <Route path="chonkie-test" element={<ChonkieTest />} />
                <Route path="agent-test" element={<AgentTest />} />
                <Route path="parse" element={<AdminParse />} />
                <Route path="workflows" element={<WorkflowList />} />
                <Route path="workflows/:workflowId" element={<WorkflowDetails />} />
                <Route path="support" element={<Support />} />
                <Route path="audit" element={<AdminAuditLogs />} />
                <Route path="settings" element={<AdminSettings />} />
              </Route>
              <Route path="*" element={<NotFound />} />
                            </Routes>
                    </AuthProvider>        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  </ErrorBoundary>
);

export default App;
