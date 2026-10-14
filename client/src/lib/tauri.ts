import type { Command } from '$lib';
import { invoke } from '@tauri-apps/api/tauri';
import { PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY } from '$env/static/public';
import { restoreAuthFromStore } from './auth';

const STORE_PATH = 'stores/store.json';

export const setStore = async (key: string, value: unknown) => {
	return await invoke('set_store', { path: STORE_PATH, key, value });
};

export const getStore = async (key: string) => {
	return await invoke('get_store', { path: STORE_PATH, key });
};

export const runCommand = async (command: Command): Promise<void> => {
	await invoke('run_command', { command: command.command });
};

/**
 * Must be called once after login (or on app start if already logged in).
 * Writes Supabase credentials to the Rust store so the Realtime backend
 * can open its WebSocket without needing env vars on the Rust side.
 * Then signals the Rust backend to (re)start its Realtime subscription.
 */
export const initRealtime = async () => {
	await restoreAuthFromStore();
	await setStore('supabaseUrl', PUBLIC_SUPABASE_URL);
	await setStore('supabaseAnonKey', PUBLIC_SUPABASE_ANON_KEY);
	await invoke('init_realtime');
};