import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Plus, Trash2, GripVertical, Save, X } from "lucide-react";
import { toast } from "sonner";

interface WorkflowStep {
  id?: string;
  step_name: string;
  step_order: number;
  agent_name: string;
  system_prompt?: string;
  allowed_tools: string[];
  execution_mode: 'sequential' | 'parallel';
  step_config?: Record<string, unknown>;
}

interface WorkflowStepEditorProps {
  workflowId: string;
  workflowName: string;
  initialSteps?: WorkflowStep[];
  availablePlugins: Array<{ id: string; name: string }>;
  availableAgents: Array<{ name: string; description: string }>;
  onSave: (steps: WorkflowStep[]) => Promise<void>;
  onCancel: () => void;
}

export function WorkflowStepEditor({
  workflowId,
  workflowName,
  initialSteps = [],
  availablePlugins,
  availableAgents,
  onSave,
  onCancel
}: WorkflowStepEditorProps) {
  const [steps, setSteps] = useState<WorkflowStep[]>(
    initialSteps.length > 0
      ? initialSteps
      : [{
          step_name: "Step 1",
          step_order: 0,
          agent_name: "",
          system_prompt: "",
          allowed_tools: [],
          execution_mode: 'sequential',
          step_config: {}
        }]
  );
  const [isSaving, setIsSaving] = useState(false);

  const addStep = () => {
    const newStep: WorkflowStep = {
      step_name: `Step ${steps.length + 1}`,
      step_order: steps.length,
      agent_name: "",
      system_prompt: "",
      allowed_tools: [],
      execution_mode: 'sequential',
      step_config: {}
    };
    setSteps([...steps, newStep]);
  };

  const removeStep = (index: number) => {
    if (steps.length === 1) {
      toast.error("Workflow must have at least one step");
      return;
    }
    const newSteps = steps.filter((_, i) => i !== index);
    // Reorder steps
    newSteps.forEach((step, i) => {
      step.step_order = i;
      if (!step.step_name.startsWith("Step ")) {
        // Keep custom names
      } else {
        step.step_name = `Step ${i + 1}`;
      }
    });
    setSteps(newSteps);
  };

  const updateStep = (index: number, field: keyof WorkflowStep, value: any) => {
    const newSteps = [...steps];
    newSteps[index] = { ...newSteps[index], [field]: value };
    setSteps(newSteps);
  };

  const togglePlugin = (stepIndex: number, pluginName: string) => {
    const newSteps = [...steps];
    const step = newSteps[stepIndex];
    const allowed = step.allowed_tools || [];
    if (allowed.includes(pluginName)) {
      step.allowed_tools = allowed.filter(t => t !== pluginName);
    } else {
      step.allowed_tools = [...allowed, pluginName];
    }
    setSteps(newSteps);
  };

  const moveStep = (index: number, direction: 'up' | 'down') => {
    if (
      (direction === 'up' && index === 0) ||
      (direction === 'down' && index === steps.length - 1)
    ) {
      return;
    }

    const newSteps = [...steps];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    [newSteps[index], newSteps[targetIndex]] = [newSteps[targetIndex], newSteps[index]];

    // Update step orders
    newSteps.forEach((step, i) => {
      step.step_order = i;
    });

    setSteps(newSteps);
  };

  const handleSave = async () => {
    // Validation
    for (const step of steps) {
      if (!step.agent_name) {
        toast.error(`Please select an agent for ${step.step_name}`);
        return;
      }
    }

    setIsSaving(true);
    try {
      await onSave(steps);
      toast.success("Workflow steps saved successfully");
    } catch (error) {
      toast.error("Failed to save workflow steps");
      console.error(error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Edit Workflow: {workflowName}</CardTitle>
          <CardDescription>
            Define the sequence of steps, agents, and tools for this workflow
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {steps.map((step, index) => (
            <Card key={index} className="border-2 border-primary/20">
              <CardHeader className="pb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex flex-col gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => moveStep(index, 'up')}
                        disabled={index === 0}
                        className="h-6 px-2"
                      >
                        ▲
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => moveStep(index, 'down')}
                        disabled={index === steps.length - 1}
                        className="h-6 px-2"
                      >
                        ▼
                      </Button>
                    </div>
                    <GripVertical className="h-5 w-5 text-muted-foreground" />
                    <Badge className="text-lg px-3 py-1">{index + 1}</Badge>
                    <Input
                      value={step.step_name}
                      onChange={(e) => updateStep(index, 'step_name', e.target.value)}
                      className="font-semibold max-w-xs"
                      placeholder="Step name"
                    />
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeStep(index)}
                    className="text-danger hover:text-danger"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Agent Selection */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Agent</Label>
                    <Select
                      value={step.agent_name}
                      onValueChange={(value) => updateStep(index, 'agent_name', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select agent" />
                      </SelectTrigger>
                      <SelectContent>
                        {availableAgents.map((agent) => (
                          <SelectItem key={agent.name} value={agent.name}>
                            {agent.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label>Execution Mode</Label>
                    <Select
                      value={step.execution_mode}
                      onValueChange={(value: any) => updateStep(index, 'execution_mode', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="sequential">Sequential</SelectItem>
                        <SelectItem value="parallel">Parallel</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* System Prompt */}
                <div>
                  <Label>System Prompt (Optional)</Label>
                  <Textarea
                    value={step.system_prompt || ''}
                    onChange={(e) => updateStep(index, 'system_prompt', e.target.value)}
                    placeholder="Custom instructions for this step..."
                    rows={3}
                    className="font-mono text-sm"
                  />
                </div>

                {/* Allowed Tools/Plugins */}
                <div>
                  <Label>Allowed Tools/Plugins</Label>
                  <div className="mt-2 grid grid-cols-2 md:grid-cols-3 gap-2 max-h-64 overflow-y-auto p-2 border rounded-md">
                    {availablePlugins.map((plugin) => (
                      <div key={plugin.id} className="flex items-center space-x-2">
                        <Checkbox
                          id={`step-${index}-plugin-${plugin.id}`}
                          checked={(step.allowed_tools || []).includes(plugin.name)}
                          onCheckedChange={() => togglePlugin(index, plugin.name)}
                        />
                        <Label
                          htmlFor={`step-${index}-plugin-${plugin.id}`}
                          className="text-sm font-normal cursor-pointer"
                        >
                          {plugin.name}
                        </Label>
                      </div>
                    ))}
                  </div>
                  {step.allowed_tools && step.allowed_tools.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {step.allowed_tools.map((tool) => (
                        <Badge key={tool} variant="secondary" className="text-xs">
                          {tool}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}

          <Button
            onClick={addStep}
            variant="outline"
            className="w-full border-dashed border-2 border-primary/30 hover:border-primary/60"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Step
          </Button>

          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button variant="outline" onClick={onCancel} disabled={isSaving}>
              <X className="h-4 w-4 mr-2" />
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={isSaving}>
              {isSaving ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Workflow
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
