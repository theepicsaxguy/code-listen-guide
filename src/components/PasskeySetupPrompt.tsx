import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import { isWebAuthnSupported } from '@/lib/webauthn';
import { useToast } from '@/hooks/use-toast';

interface PasskeySetupPromptProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function PasskeySetupPrompt({ open, onOpenChange }: PasskeySetupPromptProps) {
  const { registerPasskey } = useAuth();
  const { toast } = useToast();
  const [isRegistering, setIsRegistering] = useState(false);

  const handleSetup = async () => {
    if (!isWebAuthnSupported()) {
      toast({
        title: 'WebAuthn not supported',
        description: 'Your browser does not support passkeys. Please use a modern browser.',
        variant: 'danger',
      });
      return;
    }

    setIsRegistering(true);
    try {
      // Generate a simple device name
      const deviceName = (navigator as Navigator & { userAgentData?: { platform?: string } }).userAgentData?.platform ||
                         navigator.platform ||
                         'Device';
      const passkeyName = `${deviceName} - ${new Date().toLocaleDateString()}`;
      await registerPasskey(passkeyName);
      toast({
        title: 'Passkey set up successfully!',
        description: 'You can now use your passkey to log in securely.',
      });
      onOpenChange(false);
    } catch (error) {
      console.error('Failed to register passkey:', error);
      toast({
        title: 'Failed to set up passkey',
        description: error instanceof Error ? error.message : 'An error occurred while setting up your passkey.',
        variant: 'danger',
      });
    } finally {
      setIsRegistering(false);
    }
  };

  const handleDismiss = () => {
    // Store dismissal in localStorage so we don't show it again
    localStorage.setItem('passkey_prompt_dismissed', 'true');
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Set up a passkey for faster, more secure login</DialogTitle>
          <DialogDescription>
            Passkeys let you sign in quickly and securely using your device's biometric authentication
            (like Face ID or Touch ID) or a PIN. You won't need to remember your password as often.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="flex-col sm:flex-row gap-2">
          <Button
            variant="outline"
            onClick={handleDismiss}
            disabled={isRegistering}
          >
            Maybe later
          </Button>
          <Button
            onClick={handleSetup}
            disabled={isRegistering}
          >
            {isRegistering ? 'Setting up...' : 'Set up passkey'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

