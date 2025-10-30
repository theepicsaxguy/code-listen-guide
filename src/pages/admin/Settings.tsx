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
        <h1 className="text-3xl font-bold gradient-text-primary flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center shadow-lg shadow-primary/20">
            <SettingsIcon className="w-6 h-6 text-primary-foreground" />
          </div>
          Settings
        </h1>
        <p className="text-muted-foreground mt-2">
          Configure system settings, rate limits, and feature toggles
        </p>
      </div>

      {isLoading ? (
        <Card className="bg-card">
          <CardContent className="p-12 text-center">
            <p className="text-muted-foreground">Loading settings...</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6">
          <Card className="bg-gradient-card-primary border-primary/20 hover:border-primary/40 transition-all hover-card card-elevation">
            <CardHeader className="bg-gradient-to-r from-primary/15 to-accent/12">
              <CardTitle className="flex items-center gap-3 text-xl text-primary">
                <div className="w-10 h-10 rounded-xl bg-gradient-primary/20 flex items-center justify-center shadow-md shadow-primary/10">
                  <Shield className="h-5 w-5 icon-gradient" />
                </div>
                Rate Limits
              </CardTitle>
              <CardDescription className="text-base mt-2">API rate limiting configuration</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-gradient-stat rounded-lg hover-card">
                <span className="text-sm font-semibold text-foreground">Enabled</span>
                <Badge variant={settings?.rate_limits?.enabled ? "default" : "secondary"} className="font-bold">
                  {settings?.rate_limits?.enabled ? (
                    <span className="flex items-center gap-1.5">
                      <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
                      Active
                    </span>
                  ) : (
                    "Disabled"
                  )}
                </Badge>
              </div>
              <div className="flex justify-between items-center p-3 bg-gradient-stat rounded-lg hover-card">
                <span className="text-sm font-semibold text-foreground">Requests per minute</span>
                <span className="font-mono text-lg font-bold text-primary">{settings?.rate_limits?.requests_per_minute || "N/A"}</span>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-card-accent border-accent/20 hover:border-accent/40 transition-all hover-card card-elevation">
            <CardHeader className="bg-gradient-to-r from-accent/15 to-primary/12">
              <CardTitle className="flex items-center gap-3 text-xl text-accent">
                <div className="w-10 h-10 rounded-xl bg-gradient-accent/20 flex items-center justify-center shadow-md shadow-accent/10">
                  <Zap className="h-5 w-5 icon-gradient-accent" />
                </div>
                Features
              </CardTitle>
              <CardDescription className="text-base mt-2">System feature toggles</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-gradient-stat rounded-lg hover-card">
                <span className="text-sm font-semibold text-foreground">User Registration</span>
                <Badge variant={settings?.features?.user_registration ? "default" : "secondary"} className="font-bold">
                  {settings?.features?.user_registration ? (
                    <span className="flex items-center gap-1.5">
                      <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
                      Enabled
                    </span>
                  ) : (
                    "Disabled"
                  )}
                </Badge>
              </div>
              <div className="flex justify-between items-center p-3 bg-gradient-stat rounded-lg hover-card">
                <span className="text-sm font-semibold text-foreground">Payment Processing</span>
                <Badge variant={settings?.features?.payment_processing ? "default" : "secondary"} className="font-bold">
                  {settings?.features?.payment_processing ? (
                    <span className="flex items-center gap-1.5">
                      <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
                      Enabled
                    </span>
                  ) : (
                    "Disabled"
                  )}
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-card-secondary border-secondary/30 hover:border-secondary/50 transition-all hover-card card-elevation">
            <CardHeader className="bg-gradient-to-r from-secondary/15 to-primary/12">
              <CardTitle className="flex items-center gap-3 text-xl text-foreground">
                <div className="w-10 h-10 rounded-xl bg-gradient-secondary/20 flex items-center justify-center shadow-md shadow-secondary/10">
                  <SettingsIcon className="h-5 w-5 text-primary" />
                </div>
                System Information
              </CardTitle>
              <CardDescription className="text-base mt-2">Current system configuration</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-gradient-stat rounded-lg hover-card">
                <span className="text-sm font-semibold text-foreground">Version</span>
                <span className="font-mono text-lg font-bold gradient-text-primary">{settings?.system?.version || "N/A"}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gradient-stat rounded-lg hover-card">
                <span className="text-sm font-semibold text-foreground">Environment</span>
                <Badge variant="default" className="bg-gradient-primary text-primary-foreground font-bold shadow-md shadow-primary/20">
                  {settings?.system?.environment || "N/A"}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
