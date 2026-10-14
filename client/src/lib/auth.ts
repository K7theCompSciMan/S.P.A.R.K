import type { Session } from '@supabase/supabase-js';
import { getStore, setStore } from './tauri';
import { supabase } from './supabase';

export async function persistSession(session: Session): Promise<void> {
	await setStore('accessToken', session.access_token);
	await setStore('refreshToken', session.refresh_token);
}

/** Restore the Supabase client session from tokens stored in the Tauri store. */
export async function restoreAuthFromStore(): Promise<boolean> {
	const accessToken = await getStore('accessToken');
	const refreshToken = await getStore('refreshToken');

	if (typeof accessToken !== 'string' || !accessToken) return false;
	if (typeof refreshToken !== 'string' || !refreshToken) return false;

	const { data, error } = await supabase.auth.setSession({
		access_token: accessToken,
		refresh_token: refreshToken
	});

	if (!error && data.session) return true;

	const { data: refreshed, error: refreshError } = await supabase.auth.refreshSession({
		refresh_token: refreshToken
	});

	if (refreshError || !refreshed.session) return false;

	await persistSession(refreshed.session);
	return true;
}

export async function ensureAuthenticated(): Promise<boolean> {
	const { data: { user } } = await supabase.auth.getUser();
	if (user) return true;
	return restoreAuthFromStore();
}

export async function signOut(): Promise<void> {
	await supabase.auth.signOut();
	await setStore('accessToken', '');
	await setStore('refreshToken', '');
	await setStore('user', null);
}
