import { createClient } from '@supabase/supabase-js';
import { PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY } from '$env/static/public';

// SvelteKit with adapter-static (used by Tauri) bakes env vars at build time
// via $env/static/public — NOT import.meta.env, which is Vite-only and
// unreliable in the prerendered/static context.
// Variables must be prefixed PUBLIC_ and live in client/.env

export const supabase = createClient(PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY, {
	auth: {
		// Session tokens are persisted in the Tauri store, not browser storage.
		persistSession: false,
		autoRefreshToken: false,
		detectSessionInUrl: false
	}
});

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type Group = {
	id: string;
	name: string;
	devices: { client: string[]; server: string[] };
	messages: unknown[];
	command_presets: unknown[];
	ai_messages: unknown[];
	settings: Record<string, unknown>;
	assigned_user_id: string;
};

export type ClientDevice = {
	id: string;
	name: string;
	messages: unknown[];
	assigned_group_id: string;
	assigned_user_id: string;
	device_commands: { name: string; command: string; aliases: string[] }[];
	settings: Record<string, unknown>;
	aliases: string[];
};

export type ServerDevice = Omit<ClientDevice, 'device_commands'> & {
	device_commands: Record<string, unknown>;
};

export type Message = {
	id: string;
	from: string;
	to: string;
	content: string;
	from_device_type: string;
	status: number;
};

export type User = {
	id: string;
	email: string;
	username: string;
	settings: Record<string, unknown>;
};
