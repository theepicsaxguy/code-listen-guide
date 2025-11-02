import { useState, useMemo, useEffect } from "react";
import { Activity, Loader2, Settings, Play, Workflow, MessageSquare, Code2, Clock, CheckCircle2, XCircle, ChevronDown, ChevronRight } from "lucide-react";
import { toast } from "sonner";
// TODO: Replace apiClient calls with generated hooks from '@/lib/api/generated'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";

interface AgentInfo {
 name: string;
 description: string;
 requires_input: boolean;
 requires_chapter_data?: boolean;
 tools: string[];
}

interface AgentTestResult {
 agent_name: string;
 input_message: string;
 output_message: string;
 messages: Array<{ role: string; content: string; timestamp: number }>;
 tools_called: Array<{ tool: string; arguments: any; timestamp: number }>;
 execution_time_seconds: number;
 error?: string;
}

interface WorkflowTestResult {
 workflow_id: string;
 stages: Array<{ name: string; status: string; output?: string }>;
 final_result: Record<string, any>;
 execution_time_seconds: number;
 error?: string;
}

export default function AgentTest() {
 // Agent test state
 const [selectedAgent, setSelectedAgent] = useState<string>("analyzer");
 const [agentInput, setAgentInput] = useState<string>("Analyze the repository at https://github.com/microsoft/agent-framework and respond with JSON.");
 const [customInstructions, setCustomInstructions] = useState<string>("");
 const [chapterDataJson, setChapterDataJson] = useState<string>("{}");
 const [agentResult, setAgentResult] = useState<AgentTestResult | null>(null);
 const [isTestingAgent, setIsTestingAgent] = useState(false);

 // Workflow test state
 const [workflowType, setWorkflowType] = useState<"full" | "analysis_only" | "outline_only">("outline_only");
 const [repoUrl, setRepoUrl] = useState<string>("https://github.com/microsoft/agent-framework");
 const [gitRef, setGitRef] = useState<string>("main");
 const [depthTier, setDepthTier] = useState<string>("standard");
 const [workflowResult, setWorkflowResult] = useState<WorkflowTestResult | null>(null);
 const [isTestingWorkflow, setIsTestingWorkflow] = useState(false);

 // Available agents
 const [availableAgents, setAvailableAgents] = useState<AgentInfo[]>([]);
 const [loadingAgents, setLoadingAgents] = useState(false);

 // UI state
 const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(["messages"]));

 useEffect(() => {
 loadAvailableAgents();
 }, []);

 const loadAvailableAgents = async () => {
 setLoadingAgents(true);
 try {
 const response = await apiClient.listAvailableAgents();
 setAvailableAgents(response.agents);
 } catch (err: any) {
 toast.error(err.message || "Failed to load agents");
 } finally {
 setLoadingAgents(false);
 }
 };

 const selectedAgentInfo = useMemo(() => {
 return availableAgents.find((a) => a.name === selectedAgent);
 }, [availableAgents, selectedAgent]);

 const toggleSection = (section: string) => {
 const newExpanded = new Set(expandedSections);
 if (newExpanded.has(section)) {
 newExpanded.delete(section);
 } else {
 newExpanded.add(section);
 }
 setExpandedSections(newExpanded);
 };

 const handleTestAgent = async () => {
 if (!agentInput.trim()) {
 toast.error("Please provide an input message");
 return;
 }

 setIsTestingAgent(true);
 setAgentResult(null);

 try {
 let chapterData = undefined;
 if (selectedAgent === "script") {
 try {
 chapterData = JSON.parse(chapterDataJson);
 } catch {
 toast.error("Invalid chapter data JSON");
 setIsTestingAgent(false);
 return;
 }
 }

 const result = await apiClient.testAgent({
 agent_name: selectedAgent,
 input_message: agentInput,
 custom_instructions: customInstructions || undefined,
 chapter_data: chapterData,
 });

 setAgentResult(result);
 if (result.error) {
 toast.error(`Agent test failed: ${result.error}`);
 } else {
 toast.success(`Agent test completed in ${result.execution_time_seconds.toFixed(2)}s`);
 }
 } catch (err: any) {
 toast.error(err.message || "Failed to test agent");
 } finally {
 setIsTestingAgent(false);
 }
 };

 const handleTestWorkflow = async () => {
 if (!repoUrl.trim()) {
 toast.error("Please provide a repository URL");
 return;
 }

 setIsTestingWorkflow(true);
 setWorkflowResult(null);

 try {
 const result = await apiClient.testWorkflow({
 workflow_type: workflowType,
 repo_url: repoUrl,
 depth_tier: depthTier,
 git_ref: gitRef,
 });

 setWorkflowResult(result);
 if (result.error) {
 toast.error(`Workflow test failed: ${result.error}`);
 } else {
 toast.success(`Workflow completed in ${result.execution_time_seconds.toFixed(2)}s`);
 }
 } catch (err: any) {
 toast.error(err.message || "Failed to test workflow");
 } finally {
 setIsTestingWorkflow(false);
 }
 };

 const formatTimestamp = (timestamp: number) => {
 return new Date(timestamp * 1000).toLocaleTimeString();
 };

 return (
 <div className="p-8 space-y-8 max-w-7xl mx-auto animate-slide-up">
 {/* Header */}
 <div>
 <h1 className="text-4xl font-bold text-foreground flex items-center gap-3 mb-2">
 <div className="w-12 h-12 rounded-card bg-primary flex items-center justify-center elevation-raised">
 <Activity className="w-7 h-7 text-primary-foreground" />
 </div>
 <span className="gradient-text-primary">Agent Framework Test & Trace</span>
 </h1>
 <p className="text-muted-foreground mt-2 text-lg">
 Test individual agents and workflows with full tracing and modification capabilities
 </p>
 </div>

 <Tabs defaultValue="agent" className="space-y-6">
 <TabsList>
 <TabsTrigger value="agent">
 <Play className="w-4 h-4 mr-2" />
 Test Agent
 </TabsTrigger>
 <TabsTrigger value="workflow">
 <Workflow className="w-4 h-4 mr-2" />
 Test Workflow
 </TabsTrigger>
 </TabsList>

 {/* Agent Test Tab */}
 <TabsContent value="agent" className="space-y-6">
 {/* Configuration Card */}
 <Card className="bg-surface ">
 <CardHeader className="bg-surface">
 <CardTitle className="flex items-center gap-3 text-xl">
 <div className="w-10 h-10 rounded-card bg-primary/20 flex items-center justify-center elevation-flat">
 <Settings className="w-5 h-5 icon-gradient" />
 </div>
 Agent Configuration
 </CardTitle>
 <CardDescription className="text-base mt-2">Configure and test a single agent</CardDescription>
 </CardHeader>
 <CardContent className="space-y-6">
 {/* Agent Selection */}
 <div>
 <Label htmlFor="agent-select">Agent</Label>
 <Select value={selectedAgent} onValueChange={setSelectedAgent}>
 <SelectTrigger id="agent-select">
 <SelectValue />
 </SelectTrigger>
 <SelectContent>
 {availableAgents.map((agent) => (
 <SelectItem key={agent.name} value={agent.name}>
 {agent.name}
 </SelectItem>
 ))}
 </SelectContent>
 </Select>
 {selectedAgentInfo && (
 <div className="mt-3 p-4 bg-surface border border-accent/30 rounded-card transition-colors">
 <p className="text-sm text-foreground font-medium mb-3">{selectedAgentInfo.description}</p>
 {selectedAgentInfo.tools.length > 0 && (
 <div className="flex flex-wrap gap-2">
 {selectedAgentInfo.tools.map((tool, idx) => {
 const variants = ['default', 'outline', 'secondary'] as const;
 const variant = variants[idx % variants.length];
 return (
 <Badge key={tool} variant={variant} className="text-xs font-semibold px-3 py-1 hover:scale-105 transition-transform cursor-pointer">
 <Code2 className="w-3 h-3 mr-1" />
 {tool}
 </Badge>
 );
 })}
 </div>
 )}
 </div>
 )}
 </div>

 {/* Input Message */}
 <div>
 <Label htmlFor="agent-input">Input Message</Label>
 <Textarea
 id="agent-input"
 value={agentInput}
 onChange={(e) => setAgentInput(e.target.value)}
 placeholder="Enter the message or prompt for the agent..."
 rows={4}
 className="font-mono text-sm"
 />
 </div>

 {/* Custom Instructions (Optional) */}
 <div>
 <Label htmlFor="custom-instructions">Custom Instructions (Optional)</Label>
 <Textarea
 id="custom-instructions"
 value={customInstructions}
 onChange={(e) => setCustomInstructions(e.target.value)}
 placeholder="Override default agent instructions..."
 rows={3}
 className="font-mono text-sm"
 />
 <p className="text-xs text-muted-foreground mt-1">
 Note: Custom instructions may not work with all agent framework versions
 </p>
 </div>

 {/* Chapter Data (for script agent) */}
 {selectedAgent === "script" && (
 <div>
 <Label htmlFor="chapter-data">Chapter Data (JSON)</Label>
 <Textarea
 id="chapter-data"
 value={chapterDataJson}
 onChange={(e) => setChapterDataJson(e.target.value)}
 placeholder='{"number": 1, "title": "Introduction", ...}'
 rows={4}
 className="font-mono text-sm"
 />
 </div>
 )}

 {/* Test Button */}
 <Button 
 onClick={handleTestAgent} 
 disabled={isTestingAgent} 
 className="w-full bg-primary hover:opacity-90 text-primary-foreground rounded-card font-bold py-6 text-lg elevation-raised hover:elevation-overlay transition-all"
 >
 {isTestingAgent ? (
 <>
 <Loader2 className="w-5 h-5 mr-2 animate-spin" />
 Testing Agent...
 </>
 ) : (
 <>
 <Play className="w-5 h-5 mr-2" />
 Test Agent
 </>
 )}
 </Button>
 </CardContent>
 </Card>

 {/* Results Card */}
 {agentResult && (
          <Card className="bg-surface">
            <CardHeader
              className={`bg-surface border ${
                agentResult.error
                  ? 'border-danger/40 bg-danger/5'
                  : 'border-success/40 bg-success/5'
              }`}
            >
 <CardTitle className="flex items-center justify-between text-xl">
 <span className="flex items-center gap-3">
 <div className={`w-10 h-10 rounded-card flex items-center justify-center elevation-flat ${
 agentResult.error 
 ? 'bg-danger/20 shadow-danger/10' 
 : 'bg-success/20 shadow-success/10'
 }`}>
 <MessageSquare className={`w-5 h-5 ${
 agentResult.error ? 'text-danger' : 'text-success'
 }`} />
 </div>
 Agent Test Results
 </span>
 <Badge 
 variant={agentResult.error ? "danger" : "default"}
 className="text-sm font-bold px-4 py-1.5"
 >
 {agentResult.error ? "Error" : "Success"}
 </Badge>
 </CardTitle>
 </CardHeader>
 <CardContent className="space-y-4">
 {/* Summary */}
 <div className="grid grid-cols-3 gap-4">
 <div className="p-4 bg-surface border border-border/50 rounded-card transition-colors">
 <div className="text-sm text-muted-foreground font-medium mb-2">Execution Time</div>
 <div className="text-2xl font-bold text-foreground flex items-center gap-2">
 <Clock className="w-5 h-5 text-primary" />
 {agentResult.execution_time_seconds.toFixed(2)}s
 </div>
 </div>
 <div className="p-4 bg-surface border border-border/50 rounded-card transition-colors">
 <div className="text-sm text-muted-foreground font-medium mb-2">Messages</div>
 <div className="text-2xl font-bold text-foreground">{agentResult.messages.length}</div>
 </div>
 <div className="p-4 bg-surface border border-border/50 rounded-card transition-colors">
 <div className="text-sm text-muted-foreground font-medium mb-2">Tools Called</div>
 <div className="text-2xl font-bold text-foreground">{agentResult.tools_called.length}</div>
 </div>
 </div>

 {/* Error Display */}
 {agentResult.error && (
 <div className="p-4 bg-danger/10 rounded-card">
 <div className="flex items-start gap-2">
 <XCircle className="w-5 h-5 text-danger flex-shrink-0 mt-0.5" />
 <div>
 <div className="font-semibold text-danger">Error</div>
 <div className="text-sm text-muted-foreground mt-1">{agentResult.error}</div>
 </div>
 </div>
 </div>
 )}

 {/* Messages Trace */}
 <Collapsible open={expandedSections.has("messages")} onOpenChange={() => toggleSection("messages")}>
 <CollapsibleTrigger className="flex items-center justify-between w-full p-4 bg-primary/10 border border-primary/30 rounded-card hover:bg-primary/20 hover:border-primary/50 transition-all transition-colors">
 <span className="font-semibold text-primary flex items-center gap-2">
 <MessageSquare className="w-4 h-4" />
 Message Trace ({agentResult.messages.length})
 </span>
 {expandedSections.has("messages") ? (
 <ChevronDown className="w-4 h-4 text-primary" />
 ) : (
 <ChevronRight className="w-4 h-4 text-primary" />
 )}
 </CollapsibleTrigger>
 <CollapsibleContent>
 <div className="mt-2 space-y-2 max-h-96 overflow-y-auto">
 {agentResult.messages.map((msg, idx) => (
 <div
 key={idx}
 className={`p-4 rounded-card border ${
 msg.role === "user" 
 ? "bg-primary/10 border-primary/30" 
 : "bg-success/10 border-success/30"
 }`}
 >
 <div className="flex items-center justify-between mb-2">
 <Badge 
 variant={msg.role === "user" ? "default" : "secondary"}
 className={`font-semibold ${
 msg.role === "user" 
 ? "bg-primary text-primary-foreground" 
 : "bg-success text-success-foreground"
 }`}
 >
 {msg.role}
 </Badge>
 <span className="text-xs text-muted-foreground font-medium">{formatTimestamp(msg.timestamp)}</span>
 </div>
 <pre className="text-sm whitespace-pre-wrap font-mono text-foreground bg-secondary/20 p-3 rounded-card">{msg.content}</pre>
 </div>
 ))}
 </div>
 </CollapsibleContent>
 </Collapsible>

 {/* Tools Called */}
 {agentResult.tools_called.length > 0 && (
 <Collapsible open={expandedSections.has("tools")} onOpenChange={() => toggleSection("tools")}>
 <CollapsibleTrigger className="flex items-center justify-between w-full p-4 bg-accent/10 border border-accent/30 rounded-card hover:bg-accent/20 hover:border-accent/50 transition-all transition-colors">
 <span className="font-semibold text-accent flex items-center gap-2">
 <Code2 className="w-4 h-4" />
 Tools Called ({agentResult.tools_called.length})
 </span>
 {expandedSections.has("tools") ? (
 <ChevronDown className="w-4 h-4 text-accent" />
 ) : (
 <ChevronRight className="w-4 h-4 text-accent" />
 )}
 </CollapsibleTrigger>
 <CollapsibleContent>
 <div className="mt-2 space-y-2 max-h-96 overflow-y-auto">
 {agentResult.tools_called.map((tool, idx) => (
 <div key={idx} className="p-3 bg-muted rounded-card border">
 <div className="flex items-center justify-between mb-2">
 <Badge>
 <Code2 className="w-3 h-3 mr-1" />
 {tool.tool}
 </Badge>
 <span className="text-xs text-muted-foreground">{formatTimestamp(tool.timestamp)}</span>
 </div>
 <pre className="text-xs font-mono bg-background p-2 rounded overflow-x-auto">
 {JSON.stringify(tool.arguments, null, 2)}
 </pre>
 </div>
 ))}
 </div>
 </CollapsibleContent>
 </Collapsible>
 )}

 {/* Output Message */}
 {agentResult.output_message && (
 <Collapsible open={expandedSections.has("output")} onOpenChange={() => toggleSection("output")}>
 <CollapsibleTrigger className="flex items-center justify-between w-full p-4 bg-secondary/10 border border-secondary/30 rounded-card hover:bg-secondary/20 hover:border-secondary/50 transition-all transition-colors">
 <span className="font-semibold text-foreground flex items-center gap-2">
 <MessageSquare className="w-4 h-4 text-success" />
 Output Message
 </span>
 {expandedSections.has("output") ? (
 <ChevronDown className="w-4 h-4" />
 ) : (
 <ChevronRight className="w-4 h-4" />
 )}
 </CollapsibleTrigger>
 <CollapsibleContent>
 <div className="mt-2 p-4 bg-background rounded-card border max-h-96 overflow-y-auto">
 <pre className="text-sm whitespace-pre-wrap font-mono">{agentResult.output_message}</pre>
 </div>
 </CollapsibleContent>
 </Collapsible>
 )}
 </CardContent>
 </Card>
 )}
 </TabsContent>

 {/* Workflow Test Tab */}
 <TabsContent value="workflow" className="space-y-6">
 {/* Configuration Card */}
 <Card className="bg-surface border-accent/20 ">
 <CardHeader className="bg-surface">
 <CardTitle className="flex items-center gap-3 text-xl text-accent">
 <div className="w-10 h-10 rounded-card bg-accent/20 flex items-center justify-center elevation-flat">
 <Workflow className="w-5 h-5 icon-gradient-accent" />
 </div>
 Workflow Configuration
 </CardTitle>
 <CardDescription className="text-base mt-2">Test complete or partial workflows</CardDescription>
 </CardHeader>
 <CardContent className="space-y-6">
 {/* Workflow Type */}
 <div>
 <Label htmlFor="workflow-type">Workflow Type</Label>
 <Select value={workflowType} onValueChange={(v: any) => setWorkflowType(v)}>
 <SelectTrigger id="workflow-type">
 <SelectValue />
 </SelectTrigger>
 <SelectContent>
 <SelectItem value="analysis_only">Analysis Only</SelectItem>
 <SelectItem value="outline_only">Analysis + Outline</SelectItem>
 <SelectItem value="full">Full Workflow (truncated)</SelectItem>
 </SelectContent>
 </Select>
 </div>

 {/* Repository URL */}
 <div>
 <Label htmlFor="repo-url">Repository URL</Label>
 <Input
 id="repo-url"
 value={repoUrl}
 onChange={(e) => setRepoUrl(e.target.value)}
 placeholder="https://github.com/user/repo"
 />
 </div>

 {/* Git Ref */}
 <div>
 <Label htmlFor="git-ref">Git Ref</Label>
 <Input
 id="git-ref"
 value={gitRef}
 onChange={(e) => setGitRef(e.target.value)}
 placeholder="main"
 />
 </div>

 {/* Depth Tier */}
 <div>
 <Label htmlFor="depth-tier">Depth Tier</Label>
 <Select value={depthTier} onValueChange={setDepthTier}>
 <SelectTrigger id="depth-tier">
 <SelectValue />
 </SelectTrigger>
 <SelectContent>
 <SelectItem value="survey">Survey</SelectItem>
 <SelectItem value="standard">Standard</SelectItem>
 <SelectItem value="comprehensive">Comprehensive</SelectItem>
 </SelectContent>
 </Select>
 </div>

 {/* Test Button */}
 <Button 
 onClick={handleTestWorkflow} 
 disabled={isTestingWorkflow} 
 className="w-full bg-accent hover:opacity-90 text-accent-foreground rounded-card font-bold py-6 text-lg elevation-raised hover:elevation-overlay transition-all"
 >
 {isTestingWorkflow ? (
 <>
 <Loader2 className="w-5 h-5 mr-2 animate-spin" />
 Testing Workflow...
 </>
 ) : (
 <>
 <Workflow className="w-5 h-5 mr-2" />
 Test Workflow
 </>
 )}
 </Button>
 </CardContent>
 </Card>

 {/* Workflow Results */}
 {workflowResult && (
 <Card>
 <CardHeader>
 <CardTitle className="flex items-center justify-between">
 <span className="flex items-center gap-2">
 <Workflow className="w-5 h-5" />
 Workflow Test Results
 </span>
 <Badge variant={workflowResult.error ? "danger" : "default"}>
 {workflowResult.error ? "Error" : "Success"}
 </Badge>
 </CardTitle>
 </CardHeader>
 <CardContent className="space-y-4">
 {/* Summary */}
 <div className="grid grid-cols-2 gap-4">
 <div className="p-3 bg-muted rounded-card">
 <div className="text-sm text-muted-foreground">Execution Time</div>
 <div className="text-lg font-semibold flex items-center gap-1">
 <Clock className="w-4 h-4" />
 {workflowResult.execution_time_seconds.toFixed(2)}s
 </div>
 </div>
 <div className="p-3 bg-muted rounded-card">
 <div className="text-sm text-muted-foreground">Stages Completed</div>
 <div className="text-lg font-semibold">{workflowResult.stages.length}</div>
 </div>
 </div>

 {/* Error Display */}
 {workflowResult.error && (
 <div className="p-4 bg-danger/10 rounded-card">
 <div className="flex items-start gap-2">
 <XCircle className="w-5 h-5 text-danger flex-shrink-0 mt-0.5" />
 <div>
 <div className="font-semibold text-danger">Error</div>
 <div className="text-sm text-muted-foreground mt-1">{workflowResult.error}</div>
 </div>
 </div>
 </div>
 )}

 {/* Stages */}
 <div>
 <h3 className="font-semibold mb-3">Stages</h3>
 <div className="space-y-2">
 {workflowResult.stages.map((stage, idx) => (
 <div key={idx} className="p-3 bg-muted rounded-card border flex items-start justify-between">
 <div className="flex items-center gap-2">
 {stage.status === "completed" ? (
            <CheckCircle2 className="w-5 h-5 text-success" />
 ) : (
            <Loader2 className="w-5 h-5 text-primary animate-spin" />
 )}
 <div>
 <div className="font-semibold">{stage.name}</div>
 <Badge variant="outline" className="mt-1">
 {stage.status}
 </Badge>
 </div>
 </div>
 </div>
 ))}
 </div>
 </div>

 {/* Final Result */}
 <Collapsible open={expandedSections.has("workflow-output")} onOpenChange={() => toggleSection("workflow-output")}>
 <CollapsibleTrigger className="flex items-center justify-between w-full p-3 bg-muted rounded-card hover:bg-muted/80">
 <span className="font-semibold">Final Result</span>
 {expandedSections.has("workflow-output") ? (
 <ChevronDown className="w-4 h-4" />
 ) : (
 <ChevronRight className="w-4 h-4" />
 )}
 </CollapsibleTrigger>
 <CollapsibleContent>
 <div className="mt-2 p-4 bg-background rounded-card border max-h-96 overflow-y-auto">
 <pre className="text-sm whitespace-pre-wrap font-mono">
 {JSON.stringify(workflowResult.final_result, null, 2)}
 </pre>
 </div>
 </CollapsibleContent>
 </Collapsible>
 </CardContent>
 </Card>
 )}
 </TabsContent>
 </Tabs>
 </div>
 );
}
