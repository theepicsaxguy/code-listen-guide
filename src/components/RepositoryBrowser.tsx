import { useState, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  ChevronRight, 
  ChevronDown, 
  File, 
  Folder, 
  FolderOpen,
  Search,
  Code,
  FileText,
  Database,
  Settings,
  X
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface FileNode {
  path: string;
  language?: string;
  size_bytes: number;
  tags: string[];
  summary?: string;
  complexity?: string;
  content?: string;
  num_chunks?: number;
  total_tokens?: number;
}

export interface RepositoryBrowserProps {
  files: Record<string, FileNode>;
  onFileSelect?: (file: FileNode) => void;
  selectedPath?: string;
}

interface TreeNode {
  name: string;
  path: string;
  type: 'file' | 'folder';
  children?: TreeNode[];
  file?: FileNode;
}

export function RepositoryBrowser({ files, onFileSelect, selectedPath }: RepositoryBrowserProps) {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(['/']));
  const [searchQuery, setSearchQuery] = useState('');
  const [filterLanguage, setFilterLanguage] = useState<string | null>(null);

  // Build tree structure from flat file list
  const fileTree = useMemo(() => {
    const root: TreeNode = { name: '/', path: '/', type: 'folder', children: [] };
    
    Object.entries(files).forEach(([path, fileData]) => {
      const parts = path.split('/').filter(Boolean);
      let current = root;
      
      parts.forEach((part, index) => {
        const isLastPart = index === parts.length - 1;
        const currentPath = parts.slice(0, index + 1).join('/');
        
        if (!current.children) {
          current.children = [];
        }
        
        let child = current.children.find(c => c.name === part);
        
        if (!child) {
          child = {
            name: part,
            path: currentPath,
            type: isLastPart ? 'file' : 'folder',
            children: isLastPart ? undefined : [],
            file: isLastPart ? fileData : undefined,
          };
          current.children.push(child);
        }
        
        if (!isLastPart) {
          current = child;
        }
      });
    });
    
    // Sort: folders first, then files
    const sortTree = (node: TreeNode) => {
      if (node.children) {
        node.children.sort((a, b) => {
          if (a.type !== b.type) {
            return a.type === 'folder' ? -1 : 1;
          }
          return a.name.localeCompare(b.name);
        });
        node.children.forEach(sortTree);
      }
    };
    sortTree(root);
    
    return root;
  }, [files]);

  // Extract unique languages
  const languages = useMemo(() => {
    const langs = new Set<string>();
    Object.values(files).forEach(file => {
      if (file.language) langs.add(file.language);
    });
    return Array.from(langs).sort();
  }, [files]);

  // Filter files based on search and language
  const filteredFiles = useMemo(() => {
    return Object.entries(files).filter(([path, file]) => {
      if (searchQuery && !path.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false;
      }
      if (filterLanguage && file.language !== filterLanguage) {
        return false;
      }
      return true;
    });
  }, [files, searchQuery, filterLanguage]);

  const toggleFolder = (path: string) => {
    setExpandedFolders(prev => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  const getFileIcon = (language?: string) => {
    if (!language) return <File className="h-4 w-4" />;
    
    switch (language.toLowerCase()) {
      case 'python':
      case 'javascript':
      case 'typescript':
      case 'java':
      case 'c#':
      case 'go':
        return <Code className="h-4 w-4" />;
      case 'markdown':
      case 'text':
        return <FileText className="h-4 w-4" />;
      case 'json':
      case 'yaml':
      case 'toml':
        return <Settings className="h-4 w-4" />;
      case 'sql':
        return <Database className="h-4 w-4" />;
      default:
        return <File className="h-4 w-4" />;
    }
  };

  const getComplexityColor = (complexity?: string) => {
    switch (complexity) {
      case 'high':
        return 'danger';
      case 'medium':
        return 'default';
      case 'low':
        return 'secondary';
      default:
        return 'outline';
    }
  };

  const renderTreeNode = (node: TreeNode, depth: number = 0) => {
    if (node.type === 'folder') {
      const isExpanded = expandedFolders.has(node.path);
      const hasMatchingFiles = node.children?.some(child => 
        filteredFiles.some(([path]) => path.startsWith(child.path))
      );
      
      if (!hasMatchingFiles && searchQuery) {
        return null;
      }
      
      return (
        <div key={node.path}>
          <div
            className={cn(
              "flex items-center gap-2 py-1 px-2 hover:bg-accent rounded cursor-pointer",
              "transition-colors"
            )}
            style={{ paddingLeft: `${depth * 16 + 8}px` }}
            onClick={() => toggleFolder(node.path)}
          >
            {isExpanded ? (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            )}
            {isExpanded ? (
              <FolderOpen className="h-4 w-4 text-primary" />
            ) : (
              <Folder className="h-4 w-4 text-primary" />
            )}
            <span className="text-sm font-medium">{node.name}</span>
            {node.children && (
              <Badge variant="outline" className="ml-auto text-xs">
                {node.children.length}
              </Badge>
            )}
          </div>
          {isExpanded && node.children && (
            <div>
              {node.children.map(child => renderTreeNode(child, depth + 1))}
            </div>
          )}
        </div>
      );
    } else {
      // File node
      if (!filteredFiles.some(([path]) => path === node.path)) {
        return null;
      }
      
      const isSelected = selectedPath === node.path;
      
      return (
        <div
          key={node.path}
          className={cn(
            "flex items-center gap-2 py-2 px-3 rounded-card cursor-pointer",
            "transition-all transition-colors",
            isSelected 
              ? "bg-primary/20 border-2 border-primary/50 shadow-md shadow-primary/20" 
              : "border-2 border-transparent hover:border-primary/30 hover:bg-primary/10"
          )}
          style={{ paddingLeft: `${depth * 16 + 24}px` }}
          onClick={() => node.file && onFileSelect?.(node.file)}
        >
          <div className={cn(
            "w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0",
            isSelected 
              ? "bg-primary text-primary-foreground shadow-sm" 
              : "bg-primary/20 text-primary"
          )}>
            {getFileIcon(node.file?.language)}
          </div>
          <span className={cn(
            "text-sm truncate flex-1 font-medium",
            isSelected ? "text-foreground" : "text-foreground"
          )}>{node.name}</span>
          {node.file?.language && (
            <Badge variant={isSelected ? "default" : "outline"} className="text-xs">
              {node.file.language}
            </Badge>
          )}
          {node.file?.complexity && (
            <Badge variant={getComplexityColor(node.file.complexity)} className="text-xs">
              {node.file.complexity}
            </Badge>
          )}
        </div>
      );
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Repository Structure</CardTitle>
        <CardDescription>
          {Object.keys(files).length} files • {languages.length} languages
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted" aria-hidden="true" />
          <Input
            placeholder="Search files..."
            className="pl-10 pr-12"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <Button
              variant="ghost"
              size="icon"
              className="absolute right-2 top-2"
              onClick={() => setSearchQuery('')}
              >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>

        {/* Language Filter */}
        {languages.length > 0 && (
          <div className="flex flex-wrap gap-2">
            <Button
              variant={filterLanguage === null ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilterLanguage(null)}
            >
              All
            </Button>
            {languages.map(lang => (
              <Button
                key={lang}
                variant={filterLanguage === lang ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterLanguage(lang)}
              >
                {lang}
              </Button>
            ))}
          </div>
        )}

        {/* File Tree */}
        <ScrollArea className="max-h-pane-lg rounded-card border-default">
          <div className="p-2">
            {fileTree.children?.map(node => renderTreeNode(node, 0))}
          </div>
        </ScrollArea>

        {/* Stats */}
        <div className="text-sm text-muted">
          Showing {filteredFiles.length} of {Object.keys(files).length} files
        </div>
      </CardContent>
    </Card>
  );
}
