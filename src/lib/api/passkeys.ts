/**
 * Passkey API client functions.
 * 
 * These functions call the passkey endpoints directly.
 * Once Orval regenerates the API client, these can be replaced with generated hooks.
 */

import { customInstance } from './mutator';
import type { TokenResponse } from './generated';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface PasskeyRegistrationOptions {
  options: any;
  challenge: string;
}

export interface PasskeyRegistrationRequest {
  registration_response: any;
  challenge: string;
  name?: string;
}

export interface PasskeyRegistrationResponse {
  passkey_id: string;
  name?: string;
  message?: string;
}

export interface PasskeyAuthenticationOptions {
  options: any;
  challenge: string;
}

export interface PasskeyAuthenticationRequest {
  authentication_response: any;
  challenge: string;
  credential_id: string;
}

export interface Passkey {
  id: string;
  name?: string;
  last_used_at?: string;
  created_at: string;
  is_active: boolean;
}

/**
 * Get passkey registration options.
 */
export async function getPasskeyRegistrationOptions(
  name?: string
): Promise<PasskeyRegistrationOptions> {
  const response = await fetch(`${API_BASE}/auth/passkeys/registration/options`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
    },
    body: JSON.stringify({ name }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to get registration options' }));
    throw new Error(error.detail || 'Failed to get registration options');
  }

  return response.json();
}

/**
 * Complete passkey registration.
 */
export async function registerPasskey(
  data: PasskeyRegistrationRequest
): Promise<PasskeyRegistrationResponse> {
  const response = await fetch(`${API_BASE}/auth/passkeys/registration`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to register passkey' }));
    throw new Error(error.detail || 'Failed to register passkey');
  }

  return response.json();
}

/**
 * Get passkey authentication options.
 * @param email Optional email for traditional flow. If not provided, uses conditional UI.
 */
export async function getPasskeyAuthenticationOptions(
  email?: string
): Promise<PasskeyAuthenticationOptions> {
  const response = await fetch(`${API_BASE}/auth/passkeys/authentication/options`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(email ? { email } : {}),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to get authentication options' }));
    throw new Error(error.detail || 'Failed to get authentication options');
  }

  return response.json();
}

/**
 * Complete passkey authentication.
 */
export async function authenticatePasskey(
  data: PasskeyAuthenticationRequest
): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE}/auth/passkeys/authentication`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Authentication failed' }));
    throw new Error(error.detail || 'Authentication failed');
  }

  return response.json();
}

/**
 * List user's passkeys.
 */
export async function listPasskeys(): Promise<Passkey[]> {
  const response = await fetch(`${API_BASE}/auth/passkeys`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to list passkeys' }));
    throw new Error(error.detail || 'Failed to list passkeys');
  }

  return response.json();
}

/**
 * Delete a passkey.
 */
export async function deletePasskey(passkeyId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/auth/passkeys/${passkeyId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to delete passkey' }));
    throw new Error(error.detail || 'Failed to delete passkey');
  }
}

