import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Search, History, RotateCcw, FileText, Volume2 } from "lucide-react";

// TODO: Replace apiClient calls with generated hooks from '@/lib/api/generated'
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ContentSummary, ContentVersion } from "@/types/admin";
import { toast } from "sonner";

const statusVariant = (status: string): "success" | "warning" | "secondary" => {
  switch (status) {
    case "published":
      return "success";
    case "draft":
      return "warning";
    case "archived":
      return "secondary";
    default:
      return "secondary";
  }
};

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

  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Content Versioning</h1>
        <p className="mt-2 text-muted">Manage content versions and rollback when needed.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" aria-hidden="true" />
            Search content
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
          <Card key={content.id} className="transition-standard hover:elevation-flat">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <h3 className="font-semibold text-foreground">{content.title}</h3>
                  <p className="text-sm text-muted">ID: {content.id}</p>
                  <Badge variant={statusVariant(content.status)}>{content.status}</Badge>
                </div>
                <Button onClick={() => setSelectedContentId(content.id)} variant="outline" className="transition-standard">
                  <History className="mr-2 h-4 w-4" aria-hidden="true" />
                  View versions
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Dialog open={!!selectedContentId} onOpenChange={() => setSelectedContentId(null)}>
        <DialogContent className="max-h-pane-lg max-w-4xl overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Version history</DialogTitle>
            <DialogDescription>Review and rollback to previous versions.</DialogDescription>
          </DialogHeader>

          <div className="mt-4 space-y-4">
            {versions?.versions?.map((version: ContentVersion, index: number) => (
              <Card key={version.id}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 space-y-2">
                      <div className="flex flex-wrap items-center gap-3">
                        <Badge variant="outline">v{version.version}</Badge>
                        <Badge variant={statusVariant(version.status)}>{version.status}</Badge>
                        {index === 0 && <Badge variant="primary">Current</Badge>}
                      </div>
                      <h4 className="font-medium text-foreground">{version.title}</h4>
                      <p className="text-sm text-muted">
                        Created {new Date(version.created_at).toLocaleString()}
                      </p>
                      {version.changes ? (
                        <p className="text-sm text-muted">
                          <span className="font-semibold text-foreground">Changes:</span> {version.changes}
                        </p>
                      ) : null}
                      <div className="mt-3 flex flex-wrap gap-2">
                        {version.transcript ? (
                          <Button size="sm" variant="outline" className="transition-standard">
                            <FileText className="mr-1 h-4 w-4" aria-hidden="true" />
                            View transcript
                          </Button>
                        ) : null}
                        {version.audio_url ? (
                          <Button size="sm" variant="outline" className="transition-standard">
                            <Volume2 className="mr-1 h-4 w-4" aria-hidden="true" />
                            Play audio
                          </Button>
                        ) : null}
                      </div>
                    </div>
                    {index !== 0 ? (
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleRollback(selectedContentId!, version.id)}
                        disabled={rollbackMutation.isPending}
                        className="transition-standard"
                      >
                        <RotateCcw className="mr-2 h-4 w-4" aria-hidden="true" />
                        Rollback
                      </Button>
                    ) : null}
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
