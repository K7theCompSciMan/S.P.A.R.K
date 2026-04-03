import type { Command } from '$lib';
import { invoke } from '@tauri-apps/api/tauri';

export const setStore = async (key: string, value: unknown) => {
	return await invoke('set_store', { path: 'stores/store.json', key, value });
};

export const getStore = async (key: string) => {
	return await invoke('get_store', { path: 'stores/store.json', key });
};

export const runCommand = async (command: Command): Promise<void> => {
	await invoke('run_command', { command: command.command });
};
