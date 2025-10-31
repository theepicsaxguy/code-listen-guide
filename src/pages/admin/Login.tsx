import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Lock } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

export default function AdminLogin() {
 const [email, setEmail] = useState("");
 const [password, setPassword] = useState("");
 const [isLoading, setIsLoading] = useState(false);
 const { login, user } = useAuth();
 const navigate = useNavigate();

 // Redirect if already logged in as admin
 useEffect(() => {
 if (user?.is_admin) {
 navigate("/admin", { replace: true });
 } else if (user && !user.is_admin) {
 navigate("/dashboard", { replace: true });
 }
 }, [user, navigate]);

 const handleSubmit = async (event: React.FormEvent) => {
 event.preventDefault();
 setIsLoading(true);

 try {
 await login(email, password);
 // The login function will update the user state, useEffect will handle redirect
 } catch (error) {
 const message = error instanceof Error ? error.message : "Login failed";
 toast.error(message);
 setIsLoading(false);
 }
 };

 return (
 <div className="flex min-h-screen items-center justify-center bg-background px-4 py-8">
 <Card className="w-full max-w-md rounded-card  bg-surface">
 <CardHeader className="space-y-3 text-center">
 <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-md bg-primary/15 text-primary">
 <Lock className="h-5 w-5" />
 </div>
 <div className="space-y-1">
 <CardTitle className="text-2xl font-semibold text-text">Admin login</CardTitle>
 <CardDescription>Access the administrative dashboard using your credentials.</CardDescription>
 </div>
 </CardHeader>
 <CardContent>
 <form onSubmit={handleSubmit} className="space-y-6">
 <div className="space-y-2">
 <Label htmlFor="email">Email</Label>
 <Input
 id="email"
 type="email"
 autoComplete="username"
 placeholder="admin@example.com"
 value={email}
 onChange={(event) => setEmail(event.target.value)}
 required
 disabled={isLoading}
 />
 </div>
 <div className="space-y-2">
 <Label htmlFor="password">Password</Label>
 <Input
 id="password"
 type="password"
 autoComplete="current-password"
 value={password}
 onChange={(event) => setPassword(event.target.value)}
 required
 disabled={isLoading}
 />
 </div>
 <Button type="submit" className="w-full" disabled={isLoading}>
 {isLoading ? "Signing in…" : "Sign in"}
 </Button>
 </form>
 </CardContent>
 </Card>
 </div>
 );
}
