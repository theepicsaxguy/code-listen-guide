import {
 useEffect,
 useMemo,
 useRef,
 useState,
 type PointerEvent,
 type ReactNode,
} from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import {
 DropdownMenu,
 DropdownMenuContent,
 DropdownMenuItem,
 DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Separator } from "@/components/ui/separator";
import {
 ResizableHandle,
 ResizablePanel,
 ResizablePanelGroup,
} from "@/components/ui/resizable";
import {
 AlertTriangle,
 Archive,
 ArrowLeftRight,
 CheckCircle2,
 Circle,
 FileDown,
 FileText,
 GitBranch,
 GripVertical,
 Images,
 Info,
 Loader2,
 Mail,
 Menu,
 MessageSquareText,
 MoreHorizontal,
 PlayCircle,
 RefreshCw,
 Search,
 ServerCog,
 Trash2,
 Users,
 Zap,
 ZoomIn,
 ZoomOut,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";

import { cn } from "@/lib/utils";
import { AgentJob, AgentJobLog, AgentStats, Checkpoint, JobStage, ListAgentJobsResponse } from "@/types/agent";

type AgentMessageRole = "user" | "assistant" | "system" | "function";

type AttachmentType = "file" | "image";

interface AgentAttachment {
 id: string;
 type: AttachmentType;
 name: string;
 url: string;
 size: string;
}

interface AgentMessage {
 id: string;
 role: AgentMessageRole;
 content: string;
 createdAt: string;
 tokens: number;
 latencyMs: number;
 streaming?: boolean;
 functionCall?: {
 name: string;
 arguments: Record<string, unknown>;
 status: "pending" | "approved" | "rejected";
 reviewer?: string;
 };
 approval?: {
 status: "awaiting" | "approved" | "rejected";
 notes?: string;
 };
 attachments?: AgentAttachment[];
}

interface ViewOptions {
 showAttachments: boolean;
 autoScroll: boolean;
 compactMessages: boolean;
}

interface WorkflowNode {
 id: string;
 label: string;
 status: "pending" | "running" | "completed" | "failed";
 executor: string;
 input: string;
 output: string;
 error?: string;
}

interface WorkflowEdge {
 source: string;
 target: string;
}

interface GalleryItem {
 id: string;
 title: string;
 category: "agent" | "workflow";
 difficulty: "starter" | "intermediate" | "advanced";
 tags: string[];
 description: string;
}


const defaultConversations: Conversation[] = [
 {
 id: "conv-1",
 title: "Release notes narrator",
 status: "active",
 createdAt: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(),
 updatedAt: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
 model: "gpt-4.1",
 tools: ["code_search", "doc_summarizer"],
 environment: ["REPO_URL=github.com/code", "VOICE=alloy"],
 middleware: ["rate-limiter", "cost-tracker"],
 usage: {
 totalTokens: 18420,
 totalLatencyMs: 48200,
 },
 messages: [
 {
 id: "msg-1",
 role: "system",
 content:
 "You are a senior narrator crafting conversational release notes. Keep technical depth high but narrative friendly.",
 createdAt: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(),
 tokens: 120,
 latencyMs: 180,
 },
 {
 id: "msg-2",
 role: "user",
 content:
 "Generate a five minute audio script that highlights the new observability tooling shipping this week. Pull metrics from the repo overview dashboard and remind users about the beta flags.",
 createdAt: new Date(Date.now() - 1000 * 60 * 55).toISOString(),
 tokens: 320,
 latencyMs: 240,
 attachments: [
 {
 id: "att-1",
 type: "image",
 name: "observability-dashboard.png",
 url: "https://images.unsplash.com/photo-1556740749-887f6717d7e4?auto=format&fit=crop&w=900&q=80",
 size: "1.8 MB",
 },
 ],
 },
 {
 id: "msg-3",
 role: "assistant",
 content:
 "Starting with a quick recap of the monitoring overhaul, then weaving in the story about developers gaining live traces from the new agent console...",
 createdAt: new Date(Date.now() - 1000 * 60 * 54).toISOString(),
 tokens: 560,
 latencyMs: 1300,
 streaming: true,
 functionCall: {
 name: "fetch_repo_metrics",
 arguments: {
 timeRange: "7d",
 includeIncidents: false,
 },
 status: "approved",
 reviewer: "ops-bot",
 },
 approval: {
 status: "approved",
 notes: "Matches launch brief and tone guide.",
 },
 },
 ],
 },
 {
 id: "conv-2",
 title: "Pricing deep-dive QA",
 status: "archived",
 createdAt: new Date(Date.now() - 1000 * 60 * 60 * 26).toISOString(),
 updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 20).toISOString(),
 model: "gpt-4o-mini",
 tools: ["pricing_sheet", "segment_export"],
 environment: ["REGION=us-east", "CURRENCY=usd"],
 middleware: ["moderation", "runtime-profiler"],
 usage: {
 totalTokens: 9280,
 totalLatencyMs: 21800,
 },
 messages: [
 {
 id: "msg-4",
 role: "user",
 content: "Summarize the new premium plans and surface risks for enterprise adoption.",
 createdAt: new Date(Date.now() - 1000 * 60 * 60 * 26).toISOString(),
 tokens: 188,
 latencyMs: 220,
 },
 {
 id: "msg-5",
 role: "assistant",
 content:
 "## Pricing updates\n\n- Added **audio mastering** add-on\n- Enterprise plan now bundles unlimited rerenders\n- Usage caps doubled for Pro tier\n\nKey risks:\n1. Extended onboarding timelines for regulated teams\n2. Margins tighten on creator tier if voice swaps stay high",
 createdAt: new Date(Date.now() - 1000 * 60 * 60 * 25).toISOString(),
 tokens: 640,
 latencyMs: 1100,
 attachments: [
 {
 id: "att-2",
 type: "file",
 name: "pricing-deck.pdf",
 url: "https://example.com/pricing-deck.pdf",
 size: "4.6 MB",
 },
 ],
 },
 ],
 },
];

const defaultViewOptions: ViewOptions = {
 showAttachments: true,
 autoScroll: true,
 compactMessages: false,
};

const workflowNodes: WorkflowNode[] = [
 {
 id: "ingest",
 label: "Repo ingest",
 status: "completed",
 executor: "RepositoryAnalyzer",
 input: "https://github.com/example/core",
 output: "Parsed 142 files in 38s",
 },
 {
 id: "plan",
 label: "Outline planning",
 status: "running",
 executor: "OutlineGenerator",
 input: "analysis.json",
 output: "",
 },
 {
 id: "script",
 label: "Script drafting",
 status: "pending",
 executor: "ScriptGenerator",
 input: "outline.json",
 output: "",
 },
 {
 id: "voice",
 label: "Voice synthesis",
 status: "pending",
 executor: "AudioSynthesizer",
 input: "script.md",
 output: "",
 },
 {
 id: "post",
 label: "Post processing",
 status: "pending",
 executor: "PostProcessor",
 input: "wav segments",
 output: "",
 },
];

const workflowEdges: WorkflowEdge[] = [
 { source: "ingest", target: "plan" },
 { source: "plan", target: "script" },
 { source: "script", target: "voice" },
 { source: "voice", target: "post" },
];

const galleryItems: GalleryItem[] = [
 {
 id: "gallery-1",
 title: "Security audit triage",
 category: "agent",
 difficulty: "advanced",
 tags: ["risk", "secops", "triage"],
 description:
 "Multi-agent swarm that ingests dependency alerts, scores exploitability, and drafts mitigation playbooks for engineers.",
 },
 {
 id: "gallery-2",
 title: "Onboarding storyteller",
 category: "workflow",
 difficulty: "starter",
 tags: ["education", "narration"],
 description:
 "Delivers short audio tours for new teammates by stitching repo summaries, architectural context, and product vision notes.",
 },
 {
 id: "gallery-3",
 title: "Incident postmortem coach",
 category: "agent",
 difficulty: "intermediate",
 tags: ["sre", "analysis"],
 description:
 "Analyzes observability data, correlates Slack timelines, and proposes remediation tasks with ownership suggestions.",
 },
 {
 id: "gallery-4",
 title: "Voiceover localization",
 category: "workflow",
 difficulty: "advanced",
 tags: ["audio", "localization", "tts"],
 description:
 "Chain that translates narration, enforces glossary rules, and renders localized voice tracks with prosody adjustments.",
 },
];
const roleIconMap: Record<AgentMessageRole, ReactNode> = {
 system: <ServerCog className="h-4 w-4 text-purple-500" />,
 user: <Users className="h-4 w-4 text-sky-500" />,
 assistant: <Zap className="h-4 w-4 text-amber-500" />,
 function: <GitBranch className="h-4 w-4 text-emerald-500" />,
};

const roleLabelMap: Record<AgentMessageRole, string> = {
 system: "System",
 user: "User",
 assistant: "Assistant",
 function: "Function",
};

const statusBadgeStyles: Record<Conversation["status"], string> = {
 active: "bg-emerald-500/10 text-emerald-500",
 archived: "bg-muted text-muted-foreground",
 draft: "bg-sky-500/10 text-sky-500",
};

const nodeStatusStyles: Record<WorkflowNode["status"], string> = {
 pending: "bg-muted text-muted-foreground",
 running: "bg-blue-500/10 text-blue-500",
 completed: "bg-emerald-500/10 text-emerald-500",
 failed: "bg-danger/10 text-danger",
};

const difficultyStyles: Record<GalleryItem["difficulty"], string> = {
 starter: "bg-emerald-500/10 text-emerald-500",
 intermediate: "bg-sky-500/10 text-sky-500",
 advanced: "bg-amber-500/10 text-amber-500",
};

interface InlinePattern {
 regex: RegExp;
 recursive: boolean;
 render: (content: ReactNode[], key: string) => ReactNode;
}

const inlinePatterns: InlinePattern[] = [
 {
 regex: /\*\*(.+?)\*\*/,
 recursive: true,
 render: (content, key) => (
 <strong key={key} className="font-semibold">
 {content}
 </strong>
 ),
 },
 {
 regex: /`([^`]+)`/,
 recursive: false,
 render: (content, key) => (
 <code
 key={key}
 className="rounded bg-muted px-1 py-0.5 font-mono text-xs text-muted-foreground"
 >
 {content}
 </code>
 ),
 },
 {
 regex: /\*(.+?)\*/,
 recursive: true,
 render: (content, key) => (
 <em key={key} className="italic">
 {content}
 </em>
 ),
 },
];

const renderInlineMarkdown = (text: string): ReactNode[] => {
 if (!text) {
 return [];
 }

 let earliestMatch: RegExpMatchArray | null = null;
 let pattern: InlinePattern | null = null;

 inlinePatterns.forEach((candidate) => {
 const match = candidate.regex.exec(text);
 if (!match) {
 return;
 }
 if (!earliestMatch || (match.index ?? 0) < (earliestMatch.index ?? 0)) {
 earliestMatch = match;
 pattern = candidate;
 }
 });

 if (!earliestMatch || !pattern) {
 return [text];
 }

 const start = earliestMatch.index ?? 0;
 const end = start + earliestMatch[0].length;
 const before = text.slice(0, start);
 const after = text.slice(end);
 const matchContent = earliestMatch[1] ?? "";
 const key = `${pattern.regex.source}-${start}-${end}`;

 const nodes: ReactNode[] = [];
 nodes.push(...renderInlineMarkdown(before));

 const inner = pattern.recursive ? renderInlineMarkdown(matchContent) : [matchContent];
 nodes.push(pattern.render(inner, key));

 nodes.push(...renderInlineMarkdown(after));
 return nodes;
};

const renderMarkdown = (content: string): ReactNode[] => {
 const lines = content.split(/\n+/);
 const elements: ReactNode[] = [];
 let listBuffer: string[] = [];
 let orderedListBuffer: string[] = [];

 const flushLists = () => {
 if (listBuffer.length > 0) {
 const key = `ul-${elements.length}`;
 elements.push(
 <ul className="list-disc space-y-1 pl-5" key={key}>
 {listBuffer.map((item, index) => (
 <li key={`${key}-${index}`}>{renderInlineMarkdown(item)}</li>
 ))}
 </ul>,
 );
 listBuffer = [];
 }
 if (orderedListBuffer.length > 0) {
 const key = `ol-${elements.length}`;
 elements.push(
 <ol className="list-decimal space-y-1 pl-5" key={key}>
 {orderedListBuffer.map((item, index) => (
 <li key={`${key}-${index}`}>{renderInlineMarkdown(item)}</li>
 ))}
 </ol>,
 );
 orderedListBuffer = [];
 }
 };

 lines.forEach((line) => {
 if (line.trim().startsWith("- ")) {
 listBuffer.push(line.trim().slice(2));
 return;
 }

 const orderedMatch = line.trim().match(/^\d+\.\s+(.*)$/);
 if (orderedMatch) {
 orderedListBuffer.push(orderedMatch[1]);
 return;
 }

 flushLists();

 if (line.startsWith("### ")) {
 elements.push(
 <h3 className="text-lg font-semibold" key={`h3-${elements.length}`}>
 {renderInlineMarkdown(line.replace("### ", ""))}
 </h3>,
 );
 return;
 }
 if (line.startsWith("## ")) {
 elements.push(
 <h2 className="text-xl font-semibold" key={`h2-${elements.length}`}>
 {renderInlineMarkdown(line.replace("## ", ""))}
 </h2>,
 );
 return;
 }
 if (line.startsWith("# ")) {
 elements.push(
 <h1 className="text-2xl font-bold" key={`h1-${elements.length}`}>
 {renderInlineMarkdown(line.replace("# ", ""))}
 </h1>,
 );
 return;
 }

 if (line.trim().length === 0) {
 elements.push(<div className="h-2" key={`spacer-${elements.length}`} />);
 return;
 }

 elements.push(
 <p className="leading-relaxed" key={`p-${elements.length}`}>
 {renderInlineMarkdown(line)}
 </p>,
 );
 });

 flushLists();
 return elements;
};

const formatLatency = (ms: number) => {
 if (ms < 1000) {
 return `${ms} ms`;
 }
 return `${(ms / 1000).toFixed(1)} s`;
};

const formatTokens = (tokens: number) => tokens.toLocaleString();

const usePersistentState = <T,>(key: string, initialValue: T) => {
 const [state, setState] = useState<T>(() => {
 if (typeof window === "undefined") {
 return initialValue;
 }
 try {
 const stored = window.localStorage.getItem(key);
 return stored ? (JSON.parse(stored) as T) : initialValue;
 } catch (error) {
 console.error(error);
 return initialValue;
 }
 });

 useEffect(() => {
 if (typeof window === "undefined") {
 return;
 }
 window.localStorage.setItem(key, JSON.stringify(state));
 }, [key, state]);

 return [state, setState] as const;
};

const initialNodePositions: Record<string, { x: number; y: number }> = {
 ingest: { x: -280, y: 40 },
 plan: { x: -80, y: -80 },
 script: { x: 120, y: 0 },
 voice: { x: 320, y: 80 },
 post: { x: 520, y: 20 },
};
export default function AdminAgents() {
 const [conversations, setConversations] = usePersistentState<Conversation[]>(
 STORAGE_KEY_CONVERSATIONS,
 defaultConversations,
 );
 const [selectedConversationId, setSelectedConversationId] = usePersistentState<string | null>(
 STORAGE_KEY_SELECTED,
 defaultConversations[0]?.id ?? null,
 );
 const [viewOptions, setViewOptions] = usePersistentState<ViewOptions>(
 STORAGE_KEY_OPTIONS,
 defaultViewOptions,
 );
 const [streamingContent, setStreamingContent] = useState<Record<string, string>>({});
 const [selectedWorkflowNodeId, setSelectedWorkflowNodeId] = useState<string>(workflowNodes[0].id);
 const [workflowZoom, setWorkflowZoom] = useState(1);
 const [workflowOffset, setWorkflowOffset] = useState({ x: 0, y: 0 });
 const [isPanning, setIsPanning] = useState(false);
 const [panStart, setPanStart] = useState<{ x: number; y: number } | null>(null);
 const [executionStep, setExecutionStep] = useState(0);
 const [workflowLogs, setWorkflowLogs] = useState<string[]>([
 "Initializing workflow run...",
 ]);
 const [isInstructionsOpen, setIsInstructionsOpen] = useState(false);
 const [nodePositions, setNodePositions] = useState(initialNodePositions);
 const messagesEndRef = useRef<HTMLDivElement | null>(null);

 const selectedConversation = useMemo(() => {
 const found = conversations.find((conversation) => conversation.id === selectedConversationId);
 return found ?? conversations[0] ?? null;
 }, [conversations, selectedConversationId]);

 useEffect(() => {
 if (!selectedConversation) {
 return;
 }
 selectedConversation.messages
 .filter((message) => !message.streaming)
 .forEach((message) => {
 setStreamingContent((previous) => ({
 ...previous,
 [message.id]: message.content,
 }));
 });
 }, [selectedConversation]);

 useEffect(() => {
 if (!selectedConversation) {
 return;
 }
 const streamingMessage = selectedConversation.messages.find((message) => message.streaming);
 if (!streamingMessage) {
 return;
 }

 setStreamingContent((previous) => ({
 ...previous,
 [streamingMessage.id]: previous[streamingMessage.id] ?? "",
 }));

 let index = streamingContent[streamingMessage.id]?.length ?? 0;
 const interval = window.setInterval(() => {
 index += 4;
 setStreamingContent((previous) => {
 const nextChunk = streamingMessage.content.slice(0, index);
 if (nextChunk.length >= streamingMessage.content.length) {
 window.clearInterval(interval);
 return {
 ...previous,
 [streamingMessage.id]: streamingMessage.content,
 };
 }
 return {
 ...previous,
 [streamingMessage.id]: nextChunk,
 };
 });
 }, 80);

 return () => window.clearInterval(interval);
 }, [selectedConversation]);

 useEffect(() => {
 if (!viewOptions.autoScroll) {
 return;
 }
 if (!messagesEndRef.current) {
 return;
 }
 messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
 }, [selectedConversation?.messages, streamingContent, viewOptions.autoScroll]);

 useEffect(() => {
 const timer = window.setInterval(() => {
 setExecutionStep((step) => (step + 1) % workflowNodes.length);
 }, 4000);
 return () => window.clearInterval(timer);
 }, []);

 useEffect(() => {
 setWorkflowLogs((logs) => {
 const baseLogs = logs.slice(-20);
 const stepLogs = [
 "Repository analyzer finished parsing symbols.",
 "Outline generator compiling chapter beats...",
 "Script generator warming model weights...",
 "Audio synthesizer reserving GPU slots...",
 "Post processor waiting for audio buffers...",
 ];
 const nextLog = stepLogs[executionStep];
 if (baseLogs[baseLogs.length - 1] === nextLog) {
 return baseLogs;
 }
 return [...baseLogs, nextLog];
 });
 }, [executionStep]);

 const totalTokens = useMemo(() => {
 if (!selectedConversation) {
 return 0;
 }
 return selectedConversation.messages.reduce((sum, message) => sum + message.tokens, 0);
 }, [selectedConversation]);

 const totalLatency = useMemo(() => {
 if (!selectedConversation) {
 return 0;
 }
 return selectedConversation.messages.reduce((sum, message) => sum + message.latencyMs, 0);
 }, [selectedConversation]);

 const handleCreateConversation = () => {
 const timestamp = new Date().toISOString();
 const newConversation: Conversation = {
 id: `conv-${Date.now()}`,
 title: "Untitled conversation",
 status: "draft",
 createdAt: timestamp,
 updatedAt: timestamp,
 model: "gpt-4.1-mini",
 tools: ["repo_search"],
 environment: ["VOICE=alloy"],
 middleware: ["token-budget"],
 usage: {
 totalTokens: 0,
 totalLatencyMs: 0,
 },
 messages: [
 {
 id: `msg-${Date.now()}`,
 role: "system",
 content: "You are drafting a new workflow. Waiting for first prompt...",
 createdAt: timestamp,
 tokens: 42,
 latencyMs: 110,
 },
 ],
 };
 setConversations((previous) => [newConversation, ...previous]);
 setSelectedConversationId(newConversation.id);
 };

 const handleDeleteConversation = (conversationId: string) => {
 const remaining = conversations.filter((conversation) => conversation.id !== conversationId);
 setConversations(remaining);
 if (selectedConversationId === conversationId) {
 setSelectedConversationId(remaining[0]?.id ?? null);
 }
 };
 const renderMessageContent = (message: AgentMessage): ReactNode => {
 if (!message.streaming) {
 return renderMarkdown(message.content).map((element, index) => <div key={index}>{element}</div>);
 }
 const current = streamingContent[message.id] ?? "";
 if (current.length === 0) {
 return (
 <div className="flex items-center gap-2 text-muted-foreground">
 <Loader2 className="h-4 w-4 animate-spin" />
 <span>Streaming response…</span>
 </div>
 );
 }
 if (current.length < message.content.length) {
 return (
 <div className="space-y-3">
 {renderMarkdown(current).map((element, index) => (
 <div key={index}>{element}</div>
 ))}
 <div className="flex items-center gap-2 text-xs text-muted-foreground">
 <Loader2 className="h-3 w-3 animate-spin" />
 <span>Generating…</span>
 </div>
 </div>
 );
 }
 return renderMarkdown(message.content).map((element, index) => <div key={index}>{element}</div>);
 };

 const handleToggleOption = (key: keyof ViewOptions) => {
 setViewOptions((previous) => ({
 ...previous,
 [key]: !previous[key],
 }));
 };

 const handlePointerDown = (event: PointerEvent<HTMLDivElement>) => {
 setIsPanning(true);
 setPanStart({ x: event.clientX - workflowOffset.x, y: event.clientY - workflowOffset.y });
 };

 const handlePointerMove = (event: PointerEvent<HTMLDivElement>) => {
 if (!isPanning || !panStart) {
 return;
 }
 setWorkflowOffset({ x: event.clientX - panStart.x, y: event.clientY - panStart.y });
 };

 const handlePointerUp = () => {
 setIsPanning(false);
 setPanStart(null);
 };

 const handleAutoLayout = () => {
 const radius = 180;
 const count = workflowNodes.length;
 const nextPositions: Record<string, { x: number; y: number }> = {};
 workflowNodes.forEach((node, index) => {
 const angle = (index / count) * Math.PI * 2;
 nextPositions[node.id] = {
 x: Math.cos(angle) * radius,
 y: Math.sin(angle) * radius,
 };
 });
 setNodePositions(nextPositions);
 setWorkflowOffset({ x: 0, y: 0 });
 setWorkflowZoom(1);
 };

 const executionStates = useMemo(() => {
 return workflowNodes.map((node, index) => {
 if (executionStep > index) {
 return { ...node, status: "completed" as const };
 }
 if (executionStep === index) {
 return { ...node, status: "running" as const };
 }
 if (executionStep === workflowNodes.length - 1 && index === workflowNodes.length - 1) {
 return { ...node, status: "failed" as const };
 }
 return node;
 });
 }, [executionStep]);

 const selectedWorkflowNode = executionStates.find((node) => node.id === selectedWorkflowNodeId) ?? executionStates[0];

 const conversationTotals = useMemo(
 () => ({
 tokens: totalTokens,
 latency: totalLatency,
 }),
 [totalLatency, totalTokens],
 );
 return (
 <div className="p-8">
 <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
 <div>
 <h1 className="text-3xl font-bold bg-primary bg-clip-text text-transparent">
 Agent Control Center
 </h1>
 <p className="mt-2 max-w-2xl text-muted-foreground">
 Monitor conversations, follow workflow execution in real time, and explore reusable agent setups without leaving the admin console.
 </p>
 </div>
 <div className="flex flex-wrap items-center gap-2">
 <Button variant="outline" onClick={handleCreateConversation} className="gap-2">
 <MessageSquareText className="h-4 w-4" />
 New conversation
 </Button>
 <Dialog open={isInstructionsOpen} onOpenChange={setIsInstructionsOpen}>
 <DialogTrigger asChild>
 <Button variant="secondary" className="gap-2">
 <Info className="h-4 w-4" />
 Setup guide
 </Button>
 </DialogTrigger>
 <DialogContent className="max-w-2xl">
 <DialogHeader>
 <DialogTitle>Local agent setup instructions</DialogTitle>
 </DialogHeader>
 <div className="space-y-4 text-sm leading-relaxed">
 <p>
 Configure the Agent Framework CLI with a service account token, then register your runtime using the onboarding command below. The console automatically discovers tools from the manifest file.
 </p>
 <Card>
 <CardHeader>
 <CardTitle className="text-base">Bootstrap commands</CardTitle>
 <CardDescription>Run from your workstation shell</CardDescription>
 </CardHeader>
 <CardContent className="space-y-2 font-mono text-xs">
 <div className="rounded bg-muted px-3 py-2">agentctl login --token $AGENT_CENTER_TOKEN</div>
 <div className="rounded bg-muted px-3 py-2">agentctl register --env prod --tools tools.yaml</div>
 <div className="rounded bg-muted px-3 py-2">agentctl tail --conversation &lt;conversation_id&gt;</div>
 </CardContent>
 <CardFooter className="text-xs text-muted-foreground">
 Need help? Email platform@codebaseaudiobook.com and we will provision a sandbox runtime.
 </CardFooter>
 </Card>
 </div>
 </DialogContent>
 </Dialog>
 </div>
 </div>

 <Card className="mt-6 bg-yellow-500/5">
 <CardContent className="py-4">
 <div className="flex items-start gap-3">
 <AlertTriangle className="h-5 w-5 text-yellow-500 mt-0.5" />
 <div>
 <p className="font-semibold text-yellow-500">Demo Mode - Mock Data</p>
 <p className="text-sm text-muted-foreground mt-1">
 This page currently displays sample agent conversations. Real agent monitoring and workflow visualization will be connected to the backend in a future update.
 </p>
 </div>
 </div>
 </CardContent>
 </Card>

 <Tabs defaultValue="agents" className="mt-8">
 <TabsList className="grid grid-cols-3 lg:w-[420px]">
 <TabsTrigger value="agents" className="gap-2">
 <Zap className="h-4 w-4" />
 Agent UI
 </TabsTrigger>
 <TabsTrigger value="workflow" className="gap-2">
 <GitBranch className="h-4 w-4" />
 Workflow UI
 </TabsTrigger>
 <TabsTrigger value="gallery" className="gap-2">
 <Images className="h-4 w-4" />
 Gallery
 </TabsTrigger>
 </TabsList>

 <TabsContent value="agents" className="mt-6">
 <ResizablePanelGroup direction="vertical" className="min-h-[720px] rounded-lg">
 <ResizablePanel defaultSize={65}>
 <div className="grid grid-cols-1 gap-6 lg:grid-cols-[320px_1fr]">
 <Card className="border-0">
 <CardHeader className="space-y-4">
 <div>
 <CardTitle className="flex items-center justify-between">
 Conversations
 <DropdownMenu>
 <DropdownMenuTrigger asChild>
 <Button variant="ghost" size="icon">
 <MoreHorizontal className="h-4 w-4" />
 </Button>
 </DropdownMenuTrigger>
 <DropdownMenuContent align="end">
 <DropdownMenuItem className="gap-2" onSelect={handleCreateConversation}>
 <MessageSquareText className="h-4 w-4" />
 Duplicate selected
 </DropdownMenuItem>
 <DropdownMenuItem className="gap-2">
 <Archive className="h-4 w-4" />
 Archive
 </DropdownMenuItem>
 </DropdownMenuContent>
 </DropdownMenu>
 </CardTitle>
 <CardDescription className="mt-2">
 Switch between live agent chats and manage archives.
 </CardDescription>
 </div>
 <div className="flex items-center gap-2">
 <Search className="h-4 w-4 text-muted-foreground" />
 <Input placeholder="Search conversations" className="h-9" />
 </div>
 </CardHeader>
 <CardContent className="px-0">
 <ScrollArea className="h-[420px] px-4">
 <div className="space-y-2">
 {conversations.map((conversation) => (
 <Button
 key={conversation.id}
 variant={conversation.id === selectedConversation?.id ? "secondary" : "ghost"}
 className="w-full justify-start gap-3"
 onClick={() => setSelectedConversationId(conversation.id)}
 >
 <div className="flex-1 text-left">
 <div className="flex items-center justify-between">
 <span className="font-medium">{conversation.title}</span>
 <Badge
 variant="outline"
 className={cn("capitalize", statusBadgeStyles[conversation.status])}
 >
 {conversation.status}
 </Badge>
 </div>
 <p className="mt-1 text-xs text-muted-foreground">
 Updated {formatDistanceToNow(new Date(conversation.updatedAt), { addSuffix: true })}
 </p>
 </div>
 <DropdownMenu>
 <DropdownMenuTrigger asChild>
 <Button variant="ghost" size="icon" className="h-8 w-8">
 <Menu className="h-4 w-4" />
 </Button>
 </DropdownMenuTrigger>
 <DropdownMenuContent align="end">
 <DropdownMenuItem
 className="gap-2"
 onSelect={() => handleDeleteConversation(conversation.id)}
 >
 <Trash2 className="h-4 w-4" />
 Delete
 </DropdownMenuItem>
 <DropdownMenuItem className="gap-2">
 <Archive className="h-4 w-4" />
 Archive
 </DropdownMenuItem>
 </DropdownMenuContent>
 </DropdownMenu>
 </Button>
 ))}
 </div>
 </ScrollArea>
 </CardContent>
 <CardFooter className="flex flex-col gap-4 bg-muted/40">
 <div className="w-full space-y-3">
 <div className="flex items-center justify-between">
 <Label htmlFor="show-attachments" className="flex items-center gap-2 text-sm">
 <FileText className="h-4 w-4" />
 Show attachments
 </Label>
 <Switch
 id="show-attachments"
 checked={viewOptions.showAttachments}
 onCheckedChange={() => handleToggleOption("showAttachments")}
 />
 </div>
 <div className="flex items-center justify-between">
 <Label htmlFor="auto-scroll" className="flex items-center gap-2 text-sm">
 <PlayCircle className="h-4 w-4" />
 Auto scroll latest
 </Label>
 <Switch
 id="auto-scroll"
 checked={viewOptions.autoScroll}
 onCheckedChange={() => handleToggleOption("autoScroll")}
 />
 </div>
 <div className="flex items-center justify-between">
 <Label htmlFor="compact-mode" className="flex items-center gap-2 text-sm">
 <GripVertical className="h-4 w-4" />
 Compact mode
 </Label>
 <Switch
 id="compact-mode"
 checked={viewOptions.compactMessages}
 onCheckedChange={() => handleToggleOption("compactMessages")}
 />
 </div>
 </div>
 </CardFooter>
 </Card>

 <Card className="border-0">
 <CardHeader className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
 <div>
 <CardTitle className="flex items-center gap-2 text-xl">
 <Circle className="h-3 w-3 fill-emerald-500 text-emerald-500" />
 Live conversation
 </CardTitle>
 <CardDescription>
 Tokens: {formatTokens(conversationTotals.tokens)} • Latency: {formatLatency(conversationTotals.latency)}
 </CardDescription>
 </div>
 {selectedConversation && (
 <Dialog>
 <DialogTrigger asChild>
 <Button variant="outline" className="gap-2">
 <Info className="h-4 w-4" />
 Agent details
 </Button>
 </DialogTrigger>
 <DialogContent className="max-w-lg">
 <DialogHeader>
 <DialogTitle>{selectedConversation.title}</DialogTitle>
 </DialogHeader>
 <div className="space-y-4">
 <div>
 <h4 className="text-sm font-semibold">Model</h4>
 <p className="mt-1 text-sm text-muted-foreground">{selectedConversation.model}</p>
 </div>
 <div>
 <h4 className="text-sm font-semibold">Tools</h4>
 <div className="mt-2 flex flex-wrap gap-2">
 {selectedConversation.tools.map((tool) => (
 <Badge key={tool} variant="outline">
 {tool}
 </Badge>
 ))}
 </div>
 </div>
 <div>
 <h4 className="text-sm font-semibold">Environment variables</h4>
 <div className="mt-2 flex flex-col gap-1">
 {selectedConversation.environment.map((env) => (
 <span key={env} className="font-mono text-xs">
 {env}
 </span>
 ))}
 </div>
 </div>
 <div>
 <h4 className="text-sm font-semibold">Middleware</h4>
 <div className="mt-2 flex flex-wrap gap-2">
 {selectedConversation.middleware.map((item) => (
 <Badge key={item} variant="secondary">
 {item}
 </Badge>
 ))}
 </div>
 </div>
 </div>
 </DialogContent>
 </Dialog>
 )}
 </CardHeader>
 <CardContent className="flex flex-col gap-6">
 <ScrollArea className="h-[420px] pr-4">
 <div className="space-y-6">
 {selectedConversation?.messages.map((message) => {
 const content = renderMessageContent(message);
 return (
 <div
 key={message.id}
 className={
 viewOptions.compactMessages
 ? "flex items-start gap-4"
 : "space-y-3 rounded-lg p-4 shadow-sm"
 }
 >
 <div className="flex items-center gap-3">
 <Avatar className="h-10 w-10 border">
 <AvatarFallback className="bg-muted text-xs uppercase">
 {roleLabelMap[message.role].slice(0, 2)}
 </AvatarFallback>
 </Avatar>
 <div>
 <div className="flex items-center gap-2 text-sm font-semibold">
 {roleIconMap[message.role]}
 {roleLabelMap[message.role]}
 <span className="text-xs font-normal text-muted-foreground">
 {formatDistanceToNow(new Date(message.createdAt), { addSuffix: true })}
 </span>
 </div>
 <div className="flex items-center gap-3 text-xs text-muted-foreground">
 <span>{formatTokens(message.tokens)} tokens</span>
 <span>•</span>
 <span>{formatLatency(message.latencyMs)}</span>
 </div>
 </div>
 </div>
 <div className={viewOptions.compactMessages ? "flex-1" : "ml-14"}>
 <div className="prose prose-sm max-w-none space-y-2 dark:prose-invert">{content}</div>
 {message.functionCall && (
 <Card className="mt-4">
 <CardHeader className="pb-2">
 <CardTitle className="flex items-center gap-2 text-sm">
 <ServerCog className="h-4 w-4" />
 Function call
 </CardTitle>
 <CardDescription>
 {message.functionCall.name} · {message.functionCall.status}
 </CardDescription>
 </CardHeader>
 <CardContent className="space-y-2">
 <div className="grid grid-cols-2 gap-2 text-xs">
 {Object.entries(message.functionCall.arguments).map(([key, value]) => (
 <div key={key} className="flex flex-col gap-1 rounded bg-muted px-2 py-1">
 <span className="font-medium">{key}</span>
 <span className="font-mono text-[11px] text-muted-foreground">
 {JSON.stringify(value)}
 </span>
 </div>
 ))}
 </div>
 {message.functionCall.reviewer && (
 <Badge variant="outline" className="gap-1">
 <Mail className="h-3 w-3" />
 Reviewed by {message.functionCall.reviewer}
 </Badge>
 )}
 </CardContent>
 </Card>
 )}
 {message.approval && (
 <Card className="mt-4 bg-emerald-500/5">
 <CardHeader className="pb-2">
 <CardTitle className="flex items-center gap-2 text-sm text-emerald-600">
 <CheckCircle2 className="h-4 w-4" />
 Approval log
 </CardTitle>
 <CardDescription className="text-emerald-600">
 Status: {message.approval.status}
 </CardDescription>
 </CardHeader>
 {message.approval.notes && (
 <CardContent>
 <p className="text-xs text-muted-foreground">{message.approval.notes}</p>
 </CardContent>
 )}
 </Card>
 )}
 {viewOptions.showAttachments && message.attachments && message.attachments.length > 0 && (
 <Collapsible className="mt-4 rounded-lg">
 <CollapsibleTrigger asChild>
 <Button variant="ghost" className="w-full justify-between">
 Attachments
 <ArrowLeftRight className="h-4 w-4" />
 </Button>
 </CollapsibleTrigger>
 <CollapsibleContent className="space-y-3 p-4">
 {message.attachments.map((attachment) => (
 <Card key={attachment.id} className="overflow-hidden">
 {attachment.type === "image" ? (
 <div className="relative h-40 w-full">
 <img
 src={attachment.url}
 alt={attachment.name}
 className="h-full w-full object-cover"
 />
 </div>
 ) : (
 <div className="flex items-center justify-between gap-3 px-4 py-3">
 <div className="flex items-center gap-3">
 <FileText className="h-4 w-4" />
 <div>
 <p className="text-sm font-medium">{attachment.name}</p>
 <p className="text-xs text-muted-foreground">{attachment.size}</p>
 </div>
 </div>
 <Button variant="outline" size="sm" asChild>
 <a
 href={attachment.url}
 target="_blank"
 rel="noopener noreferrer"
 className="gap-2"
 >
 <FileDown className="h-3 w-3" />
 Download
 </a>
 </Button>
 </div>
 )}
 </Card>
 ))}
 </CollapsibleContent>
 </Collapsible>
 )}
 </div>
 </div>
 );
 })}
 <div ref={messagesEndRef} />
 </div>
 </ScrollArea>
 </CardContent>
 </Card>
 </div>
 </ResizablePanel>
 <ResizableHandle withHandle />
 <ResizablePanel defaultSize={35} className="bg-muted/50">
 <div className="grid gap-4 p-4 lg:grid-cols-3">
 <Card className="lg:col-span-2">
 <CardHeader className="pb-3">
 <CardTitle className="flex items-center gap-2 text-sm">
 <AlertTriangle className="h-4 w-4 text-amber-500" />
 Usage tracker
 </CardTitle>
 <CardDescription>
 Monitor live token consumption and execution costs per exchange.
 </CardDescription>
 </CardHeader>
 <CardContent className="space-y-3 text-sm">
 {selectedConversation?.messages.map((message) => (
 <div key={message.id} className="flex items-center justify-between rounded px-3 py-2">
 <div className="flex items-center gap-3 text-xs font-medium">
 {roleIconMap[message.role]}
 <span>{roleLabelMap[message.role]}</span>
 </div>
 <div className="flex items-center gap-3 text-xs text-muted-foreground">
 <span>{formatTokens(message.tokens)} tokens</span>
 <Separator orientation="vertical" className="h-4" />
 <span>{formatLatency(message.latencyMs)}</span>
 </div>
 </div>
 ))}
 </CardContent>
 </Card>
 <Card>
 <CardHeader className="pb-3">
 <CardTitle className="text-sm">Session totals</CardTitle>
 </CardHeader>
 <CardContent className="space-y-2 text-sm">
 <div className="flex items-center justify-between">
 <span className="text-muted-foreground">Messages</span>
 <span>{selectedConversation?.messages.length ?? 0}</span>
 </div>
 <div className="flex items-center justify-between">
 <span className="text-muted-foreground">Tokens</span>
 <span>{formatTokens(conversationTotals.tokens)}</span>
 </div>
 <div className="flex items-center justify-between">
 <span className="text-muted-foreground">Latency</span>
 <span>{formatLatency(conversationTotals.latency)}</span>
 </div>
 <div className="flex items-center justify-between">
 <span className="text-muted-foreground">Last updated</span>
 <span>
 {selectedConversation
 ? formatDistanceToNow(new Date(selectedConversation.updatedAt), { addSuffix: true })
 : "—"}
 </span>
 </div>
 </CardContent>
 </Card>
 </div>
 </ResizablePanel>
 </ResizablePanelGroup>
 </TabsContent>
 <TabsContent value="workflow" className="mt-6">
 <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
 <Card>
 <CardHeader className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
 <div>
 <CardTitle className="flex items-center gap-2 text-xl">
 <GitBranch className="h-5 w-5" />
 Workflow graph
 </CardTitle>
 <CardDescription>
 Drag to pan, use controls to zoom, and watch node states update as execution progresses.
 </CardDescription>
 </div>
 <div className="flex flex-wrap items-center gap-2">
 <Button
 variant="outline"
 size="sm"
 className="gap-2"
 onClick={() => setWorkflowZoom((value) => Math.min(value + 0.1, 2))}
 >
 <ZoomIn className="h-4 w-4" />
 Zoom in
 </Button>
 <Button
 variant="outline"
 size="sm"
 className="gap-2"
 onClick={() => setWorkflowZoom((value) => Math.max(value - 0.1, 0.6))}
 >
 <ZoomOut className="h-4 w-4" />
 Zoom out
 </Button>
 <Button
 variant="outline"
 size="sm"
 className="gap-2"
 onClick={() => {
 setWorkflowZoom(1);
 setWorkflowOffset({ x: 0, y: 0 });
 }}
 >
 <RefreshCw className="h-4 w-4" />
 Reset view
 </Button>
 <Button variant="secondary" size="sm" className="gap-2" onClick={handleAutoLayout}>
 <ServerCog className="h-4 w-4" />
 Auto layout
 </Button>
 </div>
 </CardHeader>
 <CardContent>
 <div
 className="relative h-[420px] w-full overflow-hidden rounded-lg bg-background"
 onPointerDown={handlePointerDown}
 onPointerMove={handlePointerMove}
 onPointerUp={handlePointerUp}
 onPointerLeave={handlePointerUp}
 >
 <div
 className="absolute inset-0"
 style={{
 transform: `translate(${workflowOffset.x}px, ${workflowOffset.y}px) scale(${workflowZoom})`,
 transformOrigin: "center",
 }}
 >
 <svg viewBox="-400 -220 800 440" className="h-full w-full">
 <defs>
 <marker id="arrow" markerWidth="6" markerHeight="6" refX="6" refY="3" orient="auto">
 <path d="M0,0 L0,6 L6,3 z" className="fill-muted-foreground/60" />
 </marker>
 </defs>
 {workflowEdges.map((edge) => {
 const source = nodePositions[edge.source];
 const target = nodePositions[edge.target];
 if (!source || !target) {
 return null;
 }
 return (
 <line
 key={`${edge.source}-${edge.target}`}
 x1={source.x}
 y1={source.y}
 x2={target.x}
 y2={target.y}
 stroke="hsl(var(--muted-foreground))"
 strokeWidth={1.5}
 markerEnd="url(#arrow)"
 />
 );
 })}
 {executionStates.map((node) => {
 const position = nodePositions[node.id];
 if (!position) {
 return null;
 }
 const isSelected = selectedWorkflowNodeId === node.id;
 return (
 <g key={node.id} transform={`translate(${position.x}, ${position.y})`}>
 <circle
 r={36}
 className={cn(
 "stroke-2",
 isSelected ? "stroke-primary" : "stroke-border",
 nodeStatusStyles[node.status],
 )}
 />
 <text
 textAnchor="middle"
 y={-4}
 className="text-[10px] font-semibold uppercase tracking-wide fill-muted-foreground"
 >
 {node.label}
 </text>
 <text textAnchor="middle" y={14} className="text-[9px] fill-muted-foreground">
 {node.executor}
 </text>
 <circle
 r={46}
 className={cn(
 "fill-transparent stroke-2",
 isSelected ? "stroke-primary/60" : "stroke-transparent",
 )}
 onClick={() => setSelectedWorkflowNodeId(node.id)}
 />
 </g>
 );
 })}
 </svg>
 </div>
 </div>
 </CardContent>
 </Card>
 <div className="space-y-6">
 <Card>
 <CardHeader className="pb-3">
 <CardTitle className="flex items-center gap-2 text-sm">
 <ServerCog className="h-4 w-4" />
 Node details
 </CardTitle>
 </CardHeader>
 <CardContent className="space-y-3 text-sm">
 <div className="flex items-center justify-between">
 <span className="text-muted-foreground">Executor</span>
 <span className="font-medium">{selectedWorkflowNode.executor}</span>
 </div>
 <div className="space-y-1">
 <p className="text-muted-foreground">Input</p>
 <div className="rounded bg-muted px-3 py-2 font-mono text-xs">{selectedWorkflowNode.input || "—"}</div>
 </div>
 <div className="space-y-1">
 <p className="text-muted-foreground">Output</p>
 <div className="rounded bg-muted px-3 py-2 font-mono text-xs">{selectedWorkflowNode.output || "—"}</div>
 </div>
 {selectedWorkflowNode.error && (
 <div className="space-y-1">
 <p className="text-muted-foreground">Error</p>
 <div className="rounded bg-danger/10 px-3 py-2 text-xs text-danger">
 {selectedWorkflowNode.error}
 </div>
 </div>
 )}
 <div className="flex items-center gap-2 text-xs">
 <Circle className="h-2.5 w-2.5" />
 <span className="capitalize">{selectedWorkflowNode.status}</span>
 </div>
 </CardContent>
 </Card>
 <Card>
 <CardHeader className="pb-3">
 <CardTitle className="text-sm">Workflow metadata</CardTitle>
 </CardHeader>
 <CardContent className="space-y-2 text-xs">
 <div className="flex items-center justify-between">
 <span className="text-muted-foreground">Executors</span>
 <span>{workflowNodes.length}</span>
 </div>
 <div className="flex items-center justify-between">
 <span className="text-muted-foreground">Edges</span>
 <span>{workflowEdges.length}</span>
 </div>
 <div className="flex items-center justify-between">
 <span className="text-muted-foreground">Active step</span>
 <span>{executionStep + 1}</span>
 </div>
 <Dialog>
 <DialogTrigger asChild>
 <Button variant="link" className="px-0 text-xs">
 View environment requirements
 </Button>
 </DialogTrigger>
 <DialogContent className="max-w-lg">
 <DialogHeader>
 <DialogTitle>Workflow requirements</DialogTitle>
 </DialogHeader>
 <div className="space-y-3 text-sm">
 <p>Executors require GPU class g2-standard-4, Node 18, and ffmpeg 7. Each run provisions an encrypted temp bucket.</p>
 <p>Ensure AGENT_FRAMEWORK_API_KEY and STRIPE_SECRET are configured in the runtime environment before launching.</p>
 </div>
 </DialogContent>
 </Dialog>
 </CardContent>
 </Card>
 <Card>
 <CardHeader className="pb-3">
 <CardTitle className="flex items-center gap-2 text-sm">
 <PlayCircle className="h-4 w-4" />
 Run output
 </CardTitle>
 </CardHeader>
 <CardContent className="h-48 overflow-hidden rounded bg-muted p-3 font-mono text-xs">
 <div className="flex flex-col gap-1">
 {workflowLogs.map((log, index) => (
 <span key={`${log}-${index}`} className="text-muted-foreground">
 {log}
 </span>
 ))}
 </div>
 </CardContent>
 </Card>
 </div>
 </div>
 </TabsContent>

 <TabsContent value="gallery" className="mt-6">
 <div className="grid gap-6 lg:grid-cols-3">
 {galleryItems.map((item) => (
 <Card key={item.id} className="flex flex-col justify-between">
 <CardHeader>
 <CardTitle className="text-lg">{item.title}</CardTitle>
 <CardDescription className="flex items-center gap-2">
 <Badge variant="outline" className="capitalize">
 {item.category}
 </Badge>
 <Badge variant="outline" className={difficultyStyles[item.difficulty]}>
 {item.difficulty}
 </Badge>
 </CardDescription>
 </CardHeader>
 <CardContent className="flex-1 text-sm text-muted-foreground">
 <p>{item.description}</p>
 </CardContent>
 <CardFooter className="flex flex-wrap items-center gap-2 text-xs">
 {item.tags.map((tag) => (
 <Badge key={tag} variant="secondary">
 #{tag}
 </Badge>
 ))}
 </CardFooter>
 </Card>
 ))}
 </div>
 </TabsContent>
 </Tabs>
 </div>
 );
}
