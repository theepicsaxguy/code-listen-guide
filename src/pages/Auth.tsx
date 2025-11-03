import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import { Code2, Key } from 'lucide-react';
import { getErrorMessage } from '@/lib/error-utils';
import { isWebAuthnSupported } from '@/lib/webauthn';
import { Separator } from '@/components/ui/separator';

export default function Auth() {
  const [isLoading, setIsLoading] = useState(false);
  const [isPasskeyLoading, setIsPasskeyLoading] = useState(false);
  const { login, loginWithPasskey, register, registerPasskey, user, isLoading: isAuthLoading } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const supportsWebAuthn = isWebAuthnSupported();

  // Redirect if already authenticated
  useEffect(() => {
    if (!isAuthLoading && user) {
      navigate('/dashboard', { replace: true });
    }
  }, [user, isAuthLoading, navigate]);

  // Show loading while checking authentication
  if (isAuthLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render login form if user is authenticated (redirect will happen)
  if (user) {
    return null;
  }

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    const formData = new FormData(e.currentTarget);
    const email = formData.get('email');
    const password = formData.get('password');

    if (!email || typeof email !== 'string' || !password || typeof password !== 'string') {
      toast({
        title: 'Validation Error',
        description: 'Please enter email and password',
        variant: 'danger',
      });
      setIsLoading(false);
      return;
    }

    try {
      await login(email.trim(), password);
      toast({ title: 'Welcome back!', description: 'Successfully logged in.' });
      navigate('/dashboard');
    } catch (error) {
      toast({
        title: 'Login failed',
        description: getErrorMessage(error),
        variant: 'danger',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    const formData = new FormData(e.currentTarget);
    const name = formData.get('name');
    const email = formData.get('email');
    const password = formData.get('password');

    if (!name || typeof name !== 'string' || !email || typeof email !== 'string' || !password || typeof password !== 'string') {
      toast({
        title: 'Validation Error',
        description: 'Please fill in all fields',
        variant: 'danger',
      });
      setIsLoading(false);
      return;
    }

    try {
      await register(email.trim(), password, name.trim());
      toast({ title: 'Account created!', description: 'Welcome to Codebase Audiobook.' });
      navigate('/dashboard');
    } catch (error) {
      toast({
        title: 'Registration failed',
        description: getErrorMessage(error),
        variant: 'danger',
        duration: 6000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative">
      {/* Radial gradient accent */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent pointer-events-none" />

      <div className="w-full max-w-md space-y-6 relative z-10">
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Code2 className="h-8 w-8 text-primary" />
            <h1 className="text-3xl font-bold text-foreground">Codebase Audiobook</h1>
          </div>
          <p className="text-base text-muted-foreground">Transform repositories into audio learning experiences</p>
        </div>

        <Tabs defaultValue="login" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="login">Login</TabsTrigger>
            <TabsTrigger value="register">Register</TabsTrigger>
          </TabsList>

          <TabsContent value="login">
            <Card className="hover:shadow-xl hover:shadow-primary/10 transition-standard">
              <form onSubmit={handleLogin}>
                <CardHeader>
                  <CardTitle className="text-xl font-semibold">Login</CardTitle>
                  <CardDescription className="text-sm text-muted-foreground">Enter your credentials to access your account</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="login-email" className="text-sm font-medium">Email</Label>
                    <Input
                      id="login-email"
                      name="email"
                      type="email"
                      placeholder="you@example.com"
                      autoComplete="email"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="login-password" className="text-sm font-medium">Password</Label>
                    <Input
                      id="login-password"
                      name="password"
                      type="password"
                      placeholder="••••••••"
                      autoComplete="current-password"
                      required
                    />
                  </div>
                </CardContent>
                <CardFooter className="flex flex-col gap-3">
                  <Button type="submit" className="w-full" disabled={isLoading || isPasskeyLoading}>
                    {isLoading ? 'Logging in...' : 'Login'}
                  </Button>
                  {supportsWebAuthn && (
                    <>
                      <div className="flex items-center gap-2 w-full">
                        <Separator className="flex-1" />
                        <span className="text-xs text-muted-foreground">OR</span>
                        <Separator className="flex-1" />
                      </div>
                      <Button
                        type="button"
                        variant="outline"
                        className="w-full"
                        onClick={async () => {
                          setIsPasskeyLoading(true);
                          try {
                            // Conditional UI: no email required, browser shows all passkeys
                            await loginWithPasskey();
                            toast({ title: 'Welcome back!', description: 'Successfully logged in with passkey.' });
                            navigate('/dashboard');
                          } catch (error) {
                            toast({
                              title: 'Passkey login failed',
                              description: getErrorMessage(error),
                              variant: 'danger',
                            });
                          } finally {
                            setIsPasskeyLoading(false);
                          }
                        }}
                        disabled={isLoading || isPasskeyLoading}
                      >
                        <Key className="mr-2 h-4 w-4" />
                        {isPasskeyLoading ? 'Authenticating...' : 'Login with Passkey'}
                      </Button>
                    </>
                  )}
                </CardFooter>
              </form>
            </Card>
          </TabsContent>

          <TabsContent value="register">
            <Card className="hover:shadow-xl hover:shadow-primary/10 transition-standard">
              <form onSubmit={handleRegister}>
                <CardHeader>
                  <CardTitle className="text-xl font-semibold">Create Account</CardTitle>
                  <CardDescription className="text-sm text-muted-foreground">Get started with your first audiobook</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="register-name" className="text-sm font-medium">Name</Label>
                    <Input
                      id="register-name"
                      name="name"
                      type="text"
                      placeholder="Your name"
                      autoComplete="name"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="register-email" className="text-sm font-medium">Email</Label>
                    <Input
                      id="register-email"
                      name="email"
                      type="email"
                      placeholder="you@example.com"
                      autoComplete="email"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="register-password" className="text-sm font-medium">Password</Label>
                    <Input
                      id="register-password"
                      name="password"
                      type="password"
                      placeholder="••••••••"
                      autoComplete="new-password"
                      required
                      minLength={8}
                    />
                  </div>
                </CardContent>
                <CardFooter className="flex flex-col gap-3">
                  <Button type="submit" className="w-full" disabled={isLoading || isPasskeyLoading}>
                    {isLoading ? 'Creating account...' : 'Create Account'}
                  </Button>
                  {supportsWebAuthn && (
                    <>
                      <div className="flex items-center gap-2 w-full">
                        <Separator className="flex-1" />
                        <span className="text-xs text-muted-foreground">OR</span>
                        <Separator className="flex-1" />
                      </div>
                      <Button
                        type="button"
                        variant="outline"
                        className="w-full"
                        onClick={async () => {
                          setIsPasskeyLoading(true);
                          try {
                            const formData = new FormData(document.querySelector('form[action*="register"]') as HTMLFormElement);
                            const name = formData.get('name');
                            const email = formData.get('email');
                            if (!email || typeof email !== 'string') {
                              toast({
                                title: 'Validation Error',
                                description: 'Please enter your email first',
                                variant: 'danger',
                              });
                              return;
                            }
                            // First register with password, then register passkey
                            if (!name || typeof name !== 'string' || !formData.get('password')) {
                              toast({
                                title: 'Validation Error',
                                description: 'Please complete the form first, then you can add a passkey',
                                variant: 'danger',
                              });
                              return;
                            }
                            // Register account first
                            await register(email.trim(), formData.get('password') as string, name.trim());
                            // Then register passkey
                            await registerPasskey(`${name.trim()}'s Passkey`);
                            toast({ title: 'Account created!', description: 'Account and passkey registered successfully.' });
                            navigate('/dashboard');
                          } catch (error) {
                            toast({
                              title: 'Registration failed',
                              description: getErrorMessage(error),
                              variant: 'danger',
                              duration: 6000,
                            });
                          } finally {
                            setIsPasskeyLoading(false);
                          }
                        }}
                        disabled={isLoading || isPasskeyLoading}
                      >
                        <Key className="mr-2 h-4 w-4" />
                        {isPasskeyLoading ? 'Registering...' : 'Add Passkey (Optional)'}
                      </Button>
                    </>
                  )}
                </CardFooter>
              </form>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
