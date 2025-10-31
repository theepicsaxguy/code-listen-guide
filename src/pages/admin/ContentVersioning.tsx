import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Search, History, RotateCcw, FileText, Volume2 } from "lucide-react";
import {
 Dialog,
 DialogContent,
 DialogDescription,
 DialogHeader,
 DialogTitle,
} from "@/components/ui/dialog";
import { ContentSummary, ContentVersion } from "@/types/admin";

export default function ContentVersioning() {
 const [search, setSearch] = useState("");
 const [selectedContentId, setSelectedContentId] = useState<string | null>(null);
 const queryClient = useQueryClient();

 const { data: contentList } = useQuery({
 queryKey: ["admin-content", search],
 queryFn: () => apiClient.getContentList(1, search),
 });

 const { data: versions } = useQuery({
 queryKey: ["content-versions", selectedContentId],
 queryFn: () => apiClient.getContentVersions(selectedContentId!),
 enabled: !!selectedContentId,
 });

 const rollbackMutation = useMutation({
 mutationFn: ({ contentId, versionId }: { contentId: string; versionId: string }) =>
 apiClient.rollbackContent(contentId, versionId),
 onSuccess: () => {
 toast.success("Content rolled back successfully");
 queryClient.invalidateQueries({ queryKey: ["content-versions"] });
 },
 onError: () => toast.error("Failed to rollback content"),
 });

 const handleRollback = (contentId: string, versionId: string) => {
 if (window.confirm("Are you sure you want to rollback to this version?")) {
 rollbackMutation.mutate({ contentId, versionId });
 }
 };

 const getStatusColor = (status: string) => {
 const colors: Record<string, string> = {
 published: "bg-green-500/10 text-green-500",
 draft: "bg-yellow-500/10 text-yellow-500",
 archived: "bg-gray-500/10 text-muted-foreground",
 };
 return colors[status] || colors.draft;
 };

 return (
 <div className="p-8 space-y-6">
 <div>
 <h1 className="text-3xl font-bold bg-primary bg-clip-text text-transparent">
 Content Versioning
 </h1>
 <p className="text-muted-foreground mt-2">Manage content versions and rollback when needed</p>
 </div>

 <Card className="bg-card">
 <CardHeader>
 <CardTitle className="flex items-center gap-2">
 <Search className="h-5 w-5" />
 Search Content
 </CardTitle>
 </CardHeader>
 <CardContent>
 <Input
 placeholder="Search by title or ID..."
 value={search}
 onChange={(e) => setSearch(e.target.value)}
 className="max-w-md"
 />
 </CardContent>
 </Card>

 <div className="grid gap-4">
 {contentList?.content?.map((content: ContentSummary) => (
 <Card key={content.id} className="bg-card hover:shadow-lg transition-shadow">
 <CardContent className="p-6">
 <div className="flex items-center justify-between">
 <div className="space-y-1">
 <h3 className="font-semibold">{content.title}</h3>
 <p className="text-sm text-muted-foreground">ID: {content.id}</p>
 <Badge className={getStatusColor(content.status)}>{content.status}</Badge>
 </div>
 <Button onClick={() => setSelectedContentId(content.id)} variant="outline">
 <History className="h-4 w-4 mr-2" />
 View Versions
 </Button>
 </div>
 </CardContent>
 </Card>
 ))}
 </div>

 <Dialog open={!!selectedContentId} onOpenChange={() => setSelectedContentId(null)}>
 <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
 <DialogHeader>
 <DialogTitle>Version History</DialogTitle>
 <DialogDescription>Review and rollback to previous versions</DialogDescription>
 </DialogHeader>

 <div className="space-y-4 mt-4">
 {versions?.versions?.map((version: ContentVersion, index: number) => (
 <Card key={version.id} className="bg-card">
 <CardContent className="p-4">
 <div className="flex items-start justify-between">
 <div className="space-y-2 flex-1">
 <div className="flex items-center gap-3">
 <Badge variant="outline">v{version.version}</Badge>
 <Badge className={getStatusColor(version.status)}>{version.status}</Badge>
 {index === 0 && (
 <Badge className="bg-primary/10 text-primary">Current</Badge>
 )}
 </div>
 <h4 className="font-medium">{version.title}</h4>
 <p className="text-sm text-muted-foreground">
 Created {new Date(version.created_at).toLocaleString()}
 </p>
 {version.changes && (
 <p className="text-sm mt-2">
 <span className="text-muted-foreground">Changes: </span>
 {version.changes}
 </p>
 )}
 <div className="flex gap-2 mt-3">
 {version.transcript && (
 <Button size="sm" variant="outline">
 <FileText className="h-3 w-3 mr-1" />
 View Transcript
 </Button>
 )}
 {version.audio_url && (
 <Button size="sm" variant="outline">
 <Volume2 className="h-3 w-3 mr-1" />
 Play Audio
 </Button>
 )}
 </div>
 </div>
 {index !== 0 && (
 <Button
 size="sm"
 variant="ghost"
 onClick={() => handleRollback(selectedContentId!, version.id)}
 disabled={rollbackMutation.isPending}
 >
 <RotateCcw className="h-4 w-4 mr-2" />
 Rollback
 </Button>
 )}
 </div>
 </CardContent>
 </Card>
 ))}
 </div>
 </DialogContent>
 </Dialog>
 </div>
 );
}
