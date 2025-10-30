import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Settings as SettingsIcon, Zap, Shield } from "lucide-react";

interface SystemSettings {
  rate_limits: {
    enabled: boolean;
    requests_per_minute: number;
  };
  features: {
    user_registration: boolean;
    payment_processing: boolean;
  };
  system: {
    version: string;
    environment: string;
  };
}

export default function AdminSettings() {
  const { data: settings, isLoading } = useQuery<SystemSettings>({
    queryKey: ["admin-settings"],
    queryFn: () => apiClient.request<SystemSettings>("/admin/settings"),
  });

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground mt-1">
          Configure system settings, rate limits, and feature toggles
        </p>
      </div>

      {isLoading ? (
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="p-12 text-center">
            <p className="text-muted-foreground">Loading settings...</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6">
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Rate Limits
              </CardTitle>
              <CardDescription>API rate limiting configuration</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Enabled</span>
                <Badge variant={settings?.rate_limits?.enabled ? "default" : "secondary"}>
                  {settings?.rate_limits?.enabled ? "Active" : "Disabled"}
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Requests per minute</span>
                <span className="font-mono text-sm">{settings?.rate_limits?.requests_per_minute || "N/A"}</span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5" />
                Features
              </CardTitle>
              <CardDescription>System feature toggles</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">User Registration</span>
                <Badge variant={settings?.features?.user_registration ? "default" : "secondary"}>
                  {settings?.features?.user_registration ? "Enabled" : "Disabled"}
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Payment Processing</span>
                <Badge variant={settings?.features?.payment_processing ? "default" : "secondary"}>
                  {settings?.features?.payment_processing ? "Enabled" : "Disabled"}
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <SettingsIcon className="h-5 w-5" />
                System Information
              </CardTitle>
              <CardDescription>Current system configuration</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Version</span>
                <span className="font-mono text-sm">{settings?.system?.version || "N/A"}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Environment</span>
                <Badge variant="outline">{settings?.system?.environment || "N/A"}</Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
