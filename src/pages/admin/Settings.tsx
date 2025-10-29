import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Settings as SettingsIcon, Zap, Shield } from "lucide-react";

export default function AdminSettings() {
  const { data: settings, isLoading } = useQuery({
    queryKey: ["admin-settings"],
    queryFn: () => apiClient.request("/admin/settings"),
  });

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Settings</h1>
        <p className="text-gray-400 mt-1">
          Configure system settings, rate limits, and feature toggles
        </p>
      </div>

      {isLoading ? (
        <Card className="bg-gray-900 border-gray-800">
          <CardContent className="p-12 text-center">
            <p className="text-gray-400">Loading settings...</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6">
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <Shield className="h-5 w-5" />
                Rate Limits
              </CardTitle>
              <CardDescription className="text-gray-400">API rate limiting configuration</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-white">Enabled</span>
                <Badge variant={settings?.rate_limits?.enabled ? "default" : "secondary"}>
                  {settings?.rate_limits?.enabled ? "Active" : "Disabled"}
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-white">Requests per minute</span>
                <span className="font-mono text-sm text-gray-300">{settings?.rate_limits?.requests_per_minute || "N/A"}</span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <Zap className="h-5 w-5" />
                Features
              </CardTitle>
              <CardDescription className="text-gray-400">System feature toggles</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-white">User Registration</span>
                <Badge variant={settings?.features?.user_registration ? "default" : "secondary"}>
                  {settings?.features?.user_registration ? "Enabled" : "Disabled"}
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-white">Payment Processing</span>
                <Badge variant={settings?.features?.payment_processing ? "default" : "secondary"}>
                  {settings?.features?.payment_processing ? "Enabled" : "Disabled"}
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <SettingsIcon className="h-5 w-5" />
                System Information
              </CardTitle>
              <CardDescription className="text-gray-400">Current system configuration</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-white">Version</span>
                <span className="font-mono text-sm text-gray-300">{settings?.system?.version || "N/A"}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-white">Environment</span>
                <Badge variant="outline" className="border-gray-700">{settings?.system?.environment || "N/A"}</Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
