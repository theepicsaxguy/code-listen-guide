/**
 * WebAuthn utilities for passkey registration and authentication.
 * 
 * Provides browser-native WebAuthn API wrappers for:
 * - Passkey registration
 * - Passkey authentication
 */

interface RegistrationOptions {
  challenge: string;
  rp: {
    name: string;
    id: string;
  };
  user: {
    id: string;
    name: string;
    display_name: string;
  };
  pub_key_cred_params: Array<{
    type: string;
    alg: number;
  }>;
  authenticator_selection?: {
    authenticator_attachment?: string;
    user_verification?: string;
    require_resident_key?: boolean;
  };
  timeout?: number;
  exclude_credentials?: Array<{
    id: string;
    type: string;
    transports?: string[];
  }>;
  attestation?: 'none' | 'indirect' | 'direct';
}

interface AuthenticationOptions {
  challenge: string;
  timeout?: number;
  rp_id: string;
  allow_credentials?: Array<{
    id: string;
    type: string;
    transports?: string[];
  }>; // Optional for conditional UI
  user_verification?: string;
}

/**
 * Convert base64url string to ArrayBuffer
 */
function base64urlToArrayBuffer(base64url: string): ArrayBuffer {
  // Replace URL-safe characters with standard base64
  const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
  // Add padding if needed
  const padded = base64 + '='.repeat((4 - (base64.length % 4)) % 4);
  // Decode
  const binary = atob(padded);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
}

/**
 * Convert ArrayBuffer to base64url string
 */
function arrayBufferToBase64url(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  // Convert to base64
  const base64 = btoa(binary);
  // Convert to base64url
  return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

/**
 * Register a new passkey.
 * 
 * @param options Registration options from server
 * @returns Registration response to send to server
 */
export async function registerPasskey(
  options: RegistrationOptions
): Promise<PublicKeyCredential> {
  // Check if WebAuthn is supported
  if (!window.PublicKeyCredential) {
    throw new Error('WebAuthn is not supported in this browser');
  }

  // Convert challenge and user ID from base64url to ArrayBuffer
  const challenge = base64urlToArrayBuffer(options.challenge);
  const userId = base64urlToArrayBuffer(options.user.id);

  // Prepare public key credential creation options
  const publicKeyCredentialCreationOptions: PublicKeyCredentialCreationOptions = {
    challenge,
    rp: options.rp,
    user: {
      id: userId,
      name: options.user.name,
      displayName: options.user.display_name,
    },
    pubKeyCredParams: options.pub_key_cred_params.map((param) => ({
      type: param.type as PublicKeyCredentialType,
      alg: Number(param.alg),
    })),
    // Map authenticator_selection to proper TypeScript types
    authenticatorSelection: options.authenticator_selection ? {
      authenticatorAttachment: options.authenticator_selection.authenticator_attachment as AuthenticatorAttachment | undefined,
      userVerification: options.authenticator_selection.user_verification as UserVerificationRequirement | undefined,
      requireResidentKey: options.authenticator_selection.require_resident_key,
    } : undefined,
    timeout: options.timeout,
    attestation: options.attestation ?? 'none', // Use provided attestation or 'none' by default
  };

  // Add exclude credentials if provided
  if (options.exclude_credentials && options.exclude_credentials.length > 0) {
    publicKeyCredentialCreationOptions.excludeCredentials = options.exclude_credentials.map(
      (cred) => ({
        id: base64urlToArrayBuffer(cred.id),
        type: cred.type as PublicKeyCredentialType,
        transports: cred.transports as AuthenticatorTransport[],
      })
    );
  }

  try {
    // Create credential
    const credential = await navigator.credentials.create({
      publicKey: publicKeyCredentialCreationOptions,
    }) as PublicKeyCredential;

    if (!credential) {
      throw new Error('Failed to create credential');
    }

    return credential;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Passkey registration failed: ${error.message}`);
    }
    throw new Error('Passkey registration failed');
  }
}

/**
 * Authenticate with a passkey.
 * 
 * @param options Authentication options from server
 * @returns Authentication response to send to server
 */
export async function authenticatePasskey(
  options: AuthenticationOptions
): Promise<PublicKeyCredential> {
  // Check if WebAuthn is supported
  if (!window.PublicKeyCredential) {
    throw new Error('WebAuthn is not supported in this browser');
  }

  // Convert challenge from base64url to ArrayBuffer
  const challenge = base64urlToArrayBuffer(options.challenge);

  // Prepare public key credential request options
  const publicKeyCredentialRequestOptions: PublicKeyCredentialRequestOptions = {
    challenge,
    timeout: options.timeout,
    rpId: options.rp_id,
    userVerification: options.user_verification as UserVerificationRequirement,
    // Conditional UI: if allow_credentials is empty/undefined, browser shows all passkeys
    allowCredentials: options.allow_credentials && options.allow_credentials.length > 0
      ? options.allow_credentials.map((cred) => ({
          id: base64urlToArrayBuffer(cred.id),
          type: cred.type as PublicKeyCredentialType,
          transports: cred.transports as AuthenticatorTransport[],
        }))
      : undefined, // undefined enables conditional UI
  };

  try {
    // Get credential
    const credential = await navigator.credentials.get({
      publicKey: publicKeyCredentialRequestOptions,
    }) as PublicKeyCredential;

    if (!credential) {
      throw new Error('Failed to get credential');
    }

    return credential;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Passkey authentication failed: ${error.message}`);
    }
    throw new Error('Passkey authentication failed');
  }
}

/**
 * Convert PublicKeyCredential to JSON format for server.
 */
export function credentialToJSON(
  credential: PublicKeyCredential
): {
  id: string;
  rawId: string;
  type: string;
  response: {
    clientDataJSON: string;
    authenticatorData?: string;
    signature?: string;
    userHandle?: string | null;
    attestationObject?: string;
  };
} {
  if (!(credential.response instanceof AuthenticatorResponse)) {
    throw new Error('Invalid credential response');
  }

  const response = credential.response;
  const result: any = {
    id: credential.id,
    rawId: arrayBufferToBase64url(credential.rawId),
    type: credential.type,
    response: {
      clientDataJSON: arrayBufferToBase64url(response.clientDataJSON),
    },
  };

  // Add authentication-specific fields
  if (response instanceof AuthenticatorAssertionResponse) {
    result.response.authenticatorData = arrayBufferToBase64url(
      response.authenticatorData
    );
    result.response.signature = arrayBufferToBase64url(response.signature);
    result.response.userHandle = response.userHandle
      ? arrayBufferToBase64url(response.userHandle)
      : null;
  }

  // Add registration-specific fields
  if (response instanceof AuthenticatorAttestationResponse) {
    result.response.attestationObject = arrayBufferToBase64url(
      response.attestationObject
    );
  }

  return result;
}

/**
 * Check if WebAuthn is supported in the current browser.
 */
export function isWebAuthnSupported(): boolean {
  return !!(
    window.PublicKeyCredential &&
    navigator.credentials &&
    navigator.credentials.create &&
    navigator.credentials.get
  );
}

