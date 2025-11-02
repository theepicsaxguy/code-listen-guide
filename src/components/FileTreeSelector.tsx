import { useState } from 'react';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ChevronRight, ChevronDown, File, Folder, FolderOpen, X } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';

interface FileTreeSelectorProps {
  modules: Record<string, any>;
  selectedFiles: string[];
  excludedPatterns: string[];
  onSelectionChange: (files: string[]) => void;
  onExclusionChange: (patterns: string[]) => void;
}

interface TreeNode {
  name: string;
  path: string;
  isDirectory: boolean;
  children?: TreeNode[];
  metadata?: any;
}

export function FileTreeSelector({
  modules,
  selectedFiles,
  excludedPatterns,
  onSelectionChange,
  onExclusionChange,
}: FileTreeSelectorProps) {
  const [expandedDirs, setExpandedDirs] = useState<Set<string>>(new Set());
  const [newPattern, setNewPattern] = useState('');

  // Build tree structure from flat modules
  const buildTree = (): TreeNode[] => {
    const root: Record<string, TreeNode> = {};

    Object.entries(modules).forEach(([path, data]) => {
      const parts = path.split('/');
      let current = root;

      parts.forEach((part, index) => {
        if (!current[part]) {
          const isLast = index === parts.length - 1;
          current[part] = {
            name: part,
            path: parts.slice(0, index + 1).join('/'),
            isDirectory: !isLast,
            children: isLast ? undefined : {},
            metadata: isLast ? data : undefined,
          };
        }
        if (!current[part].isDirectory && index < parts.length - 1) {
          // Convert file to directory if needed
          current[part].isDirectory = true;
          current[part].children = {};
        }
        if (current[part].children) {
          current = current[part].children as Record<string, TreeNode>;
        }
      });
    });

    // Convert to array
    const convertToArray = (nodes: Record<string, TreeNode>): TreeNode[] => {
      return Object.values(nodes).map(node => {
        if (node.children && Object.keys(node.children).length > 0) {
          return {
            ...node,
            children: convertToArray(node.children),
          };
        }
        return node;
      }).sort((a, b) => {
        if (a.isDirectory && !b.isDirectory) return -1;
        if (!a.isDirectory && b.isDirectory) return 1;
        return a.name.localeCompare(b.name);
      });
    };

    return convertToArray(root);
  };

  const tree = buildTree();

  const toggleDirectory = (path: string) => {
    const newExpanded = new Set(expandedDirs);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedDirs(newExpanded);
  };

  const toggleFile = (path: string) => {
    const newSelected = selectedFiles.includes(path)
      ? selectedFiles.filter(f => f !== path)
      : [...selectedFiles, path];
    onSelectionChange(newSelected);
  };

  const addExclusionPattern = () => {
    if (newPattern && !excludedPatterns.includes(newPattern)) {
      onExclusionChange([...excludedPatterns, newPattern]);
      setNewPattern('');
    }
  };

  const removeExclusionPattern = (pattern: string) => {
    onExclusionChange(excludedPatterns.filter(p => p !== pattern));
  };

  const renderTree = (nodes: TreeNode[], depth = 0): JSX.Element[] => {
    return nodes.map(node => {
      const isExpanded = expandedDirs.has(node.path);
      const isSelected = selectedFiles.includes(node.path);

      return (
        <div key={node.path}>
          <div
            className="flex items-center gap-2 py-1 px-2 hover:bg-accent/50 rounded cursor-pointer"
            style={{ paddingLeft: `${depth * 20 + 8}px` }}
            onClick={() => node.isDirectory ? toggleDirectory(node.path) : toggleFile(node.path)}
          >
            {node.isDirectory ? (
              <>
                {isExpanded ? (
                  <ChevronDown className="h-4 w-4 text-muted-foreground" />
                ) : (
                  <ChevronRight className="h-4 w-4 text-muted-foreground" />
                )}
                {isExpanded ? (
                  <FolderOpen className="h-4 w-4 text-blue-500" />
                ) : (
                  <Folder className="h-4 w-4 text-blue-500" />
                )}
              </>
            ) : (
              <>
                <div className="w-4" />
                <File className="h-4 w-4 text-muted-foreground" />
              </>
            )}
            {!node.isDirectory && (
              <Checkbox
                checked={selectedFiles.length === 0 || isSelected}
                onClick={(e) => e.stopPropagation()}
                onCheckedChange={() => toggleFile(node.path)}
              />
            )}
            <Label className="flex-1 cursor-pointer text-sm">
              {node.name}
              {node.metadata?.language && (
                <Badge variant="outline" className="ml-2 text-xs">
                  {node.metadata.language}
                </Badge>
              )}
            </Label>
          </div>
          {node.isDirectory && isExpanded && node.children && (
            <div>
              {renderTree(node.children, depth + 1)}
            </div>
          )}
        </div>
      );
    });
  };

  return (
    <div className="space-y-4">
      {/* Exclusion Patterns */}
      <div>
        <Label className="text-sm font-medium mb-2 block">Exclusion Patterns (glob)</Label>
        <div className="flex gap-2 mb-2">
          <Input
            placeholder="e.g., *.test.ts or node_modules/**"
            value={newPattern}
            onChange={(e) => setNewPattern(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && addExclusionPattern()}
          />
          <Button onClick={addExclusionPattern} variant="outline" size="sm">
            Add
          </Button>
        </div>
        <div className="flex flex-wrap gap-2">
          {excludedPatterns.map(pattern => (
            <Badge key={pattern} variant="secondary" className="gap-1">
              {pattern}
              <X
                className="h-3 w-3 cursor-pointer hover:text-destructive"
                onClick={() => removeExclusionPattern(pattern)}
              />
            </Badge>
          ))}
        </div>
      </div>

      {/* File Tree */}
      <div>
        <Label className="text-sm font-medium mb-2 block">
          File Tree (click to select/deselect specific files)
        </Label>
        <ScrollArea className="h-[400px] border rounded-md p-2">
          {renderTree(tree)}
        </ScrollArea>
        <p className="text-xs text-muted-foreground mt-2">
          {selectedFiles.length === 0 
            ? 'All files included by default (excluding patterns above)' 
            : `${selectedFiles.length} files explicitly selected`}
        </p>
      </div>
    </div>
  );
}
