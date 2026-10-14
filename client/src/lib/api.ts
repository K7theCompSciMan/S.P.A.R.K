import { deviceToSpecificDevice, type Device, type PublicUser } from '$lib';
import { ensureAuthenticated, persistSession } from './auth';
import { setStore, initRealtime } from './tauri';
import { supabase } from './supabase';

// ---------------------------------------------------------------------------
// Auth helpers
// ---------------------------------------------------------------------------

async function fetchUserProfile(userId: string) {
	const { data, error } = await supabase
		.from('users')
		.select('id, email, username, settings')
		.eq('id', userId)
		.single();

	if (error) return null;
	return data;
}

function toPublicUser(
	authUser: { id: string; email?: string; user_metadata?: Record<string, unknown> },
	profile: { id: string; email?: string; username?: string; settings?: PublicUser['settings'] } | null,
	fallback?: { email?: string; username?: string }
): PublicUser {
	const defaultSettings = { primaryCommunicationMethod: 'realtime' as const };
	return {
		id: authUser.id,
		email:
			profile?.email ??
			authUser.email ??
			fallback?.email ??
			(typeof authUser.user_metadata?.email === 'string' ? authUser.user_metadata.email : ''),
		username:
			profile?.username ??
			(typeof authUser.user_metadata?.username === 'string'
				? authUser.user_metadata.username
				: fallback?.username ?? ''),
		settings: profile?.settings ?? defaultSettings
	};
}

async function authSuccessResponse(
	session: NonNullable<Awaited<ReturnType<typeof supabase.auth.signInWithPassword>>['data']['session']>,
	fallback?: { email?: string; username?: string }
): Promise<Response> {
	await persistSession(session);

	const profile = await fetchUserProfile(session.user.id);
	const user = toPublicUser(session.user, profile, fallback);

	await setStore('user', user);
	await initRealtime();

	return new Response(
		JSON.stringify({
			user,
			accessToken: session.access_token,
			refreshToken: session.refresh_token
		}),
		{ status: 200 }
	);
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export async function loginApi(email: string, password: string): Promise<Response> {
	const normalizedEmail = email.trim().toLowerCase();
	if (!normalizedEmail || !password) {
		return new Response(JSON.stringify({ error: 'Email and password are required' }), {
			status: 400
		});
	}

	const { data, error } = await supabase.auth.signInWithPassword({
		email: normalizedEmail,
		password
	});

	if (error || !data.session) {
		return new Response(JSON.stringify({ error: error?.message ?? 'Invalid credentials' }), {
			status: 401
		});
	}

	return authSuccessResponse(data.session, { email: normalizedEmail });
}

export async function registerApi(
	email: string,
	username: string,
	password: string
): Promise<Response> {
	const normalizedEmail = email.trim().toLowerCase();
	const normalizedUsername = username.trim();

	if (!normalizedEmail || !normalizedUsername || !password) {
		return new Response(JSON.stringify({ error: 'Email, username, and password are required' }), {
			status: 400
		});
	}

	const { data, error } = await supabase.auth.signUp({
		email: normalizedEmail,
		password,
		options: {
			data: { username: normalizedUsername }
		}
	});

	if (error || !data.user) {
		return new Response(JSON.stringify({ error: error?.message ?? 'Registration failed' }), {
			status: 400
		});
	}

	let session = data.session;

	// signUp may omit the session even when email confirmation is off; sign in immediately.
	if (!session) {
		const signIn = await supabase.auth.signInWithPassword({
			email: normalizedEmail,
			password
		});

		if (signIn.error || !signIn.data.session) {
			return new Response(
				JSON.stringify({
					error:
						signIn.error?.message ??
						'Account was created but sign-in failed. Re-run client/supabase/schema.sql (auto-confirm trigger) and disable "Confirm email" under Authentication → Providers → Email.'
				}),
				{ status: 400 }
			);
		}

		session = signIn.data.session;
	}

	// Profile row is created by private.handle_new_user trigger.
	let profile = await fetchUserProfile(data.user.id);
	if (!profile) {
		await new Promise((r) => setTimeout(r, 500));
		profile = await fetchUserProfile(data.user.id);
	}

	if (!profile) {
		return new Response(
			JSON.stringify({
				error: 'Account created but profile was not found. Re-run client/supabase/schema.sql.'
			}),
			{ status: 500 }
		);
	}

	return authSuccessResponse(session, { email: normalizedEmail, username: normalizedUsername });
}

export async function sessionRefreshApi(refreshToken: string): Promise<Response> {
	const { data, error } = await supabase.auth.refreshSession({ refresh_token: refreshToken });
	if (error || !data.session) {
		return new Response(JSON.stringify({ error: error?.message ?? 'Invalid refresh token' }), {
			status: 401
		});
	}

	await persistSession(data.session);

	return new Response(
		JSON.stringify({
			accessToken: data.session.access_token,
			refreshToken: data.session.refresh_token
		}),
		{ status: 200 }
	);
}

export async function sessionUserApi(accessToken: string): Promise<Response> {
	const { data, error } = await supabase.auth.getUser(accessToken);
	if (error || !data.user) {
		return new Response(JSON.stringify({ error: 'Invalid token' }), { status: 401 });
	}

	const profile = await fetchUserProfile(data.user.id);
	if (!profile) {
		return new Response(JSON.stringify({ error: 'User profile not found' }), { status: 404 });
	}

	return new Response(JSON.stringify(toPublicUser(data.user, profile)), { status: 200 });
}

// ---------------------------------------------------------------------------
// User
// ---------------------------------------------------------------------------

export async function updateUserApi(user: PublicUser, _token: string): Promise<Response> {
	if (!(await ensureAuthenticated())) {
		return new Response(JSON.stringify({ error: 'Not authenticated' }), { status: 401 });
	}

	const { error } = await supabase
		.from('users')
		.update({ username: user.username, email: user.email, settings: user.settings })
		.eq('id', user.id);

	if (error) return new Response(JSON.stringify({ error: error.message }), { status: 500 });
	return new Response(JSON.stringify(user), { status: 200 });
}

// ---------------------------------------------------------------------------
// Groups
// ---------------------------------------------------------------------------

export async function fetchUserGroups(userId: string, _token: string): Promise<Response> {
	if (!(await ensureAuthenticated())) {
		return new Response(JSON.stringify({ error: 'Not authenticated' }), { status: 401 });
	}

	const { data, error } = await supabase
		.from('groups')
		.select('*')
		.eq('assigned_user_id', userId);

	if (error) return new Response(JSON.stringify({ error: error.message }), { status: 500 });
	return new Response(JSON.stringify(data ?? []), { status: 200 });
}

export async function fetchGroupById(groupId: string, _token: string): Promise<Response> {
	if (!(await ensureAuthenticated())) {
		return new Response(JSON.stringify({ error: 'Not authenticated' }), { status: 401 });
	}

	const { data, error } = await supabase.from('groups').select('*').eq('id', groupId).single();
	if (error) return new Response(JSON.stringify({ error: error.message }), { status: 404 });
	return new Response(JSON.stringify(data), { status: 200 });
}

export async function createGroupApi(name: string, _token: string): Promise<Response> {
	if (!(await ensureAuthenticated())) {
		return new Response(JSON.stringify({ error: 'Not authenticated' }), { status: 401 });
	}

	const {
		data: { user }
	} = await supabase.auth.getUser();

	if (!user) {
		return new Response(JSON.stringify({ error: 'Not authenticated' }), { status: 401 });
	}

	const { data, error } = await supabase
		.from('groups')
		.insert({
			name,
			assigned_user_id: user.id,
			devices: { client: [], server: [] },
			messages: [],
			command_presets: [],
			ai_messages: [],
			settings: {}
		})
		.select()
		.single();

	if (error) return new Response(JSON.stringify({ error: error.message }), { status: 500 });
	return new Response(JSON.stringify(data), { status: 200 });
}

export async function deleteGroupApi(groupId: string, _token: string): Promise<Response> {
	if (!(await ensureAuthenticated())) {
		return new Response(JSON.stringify({ error: 'Not authenticated' }), { status: 401 });
	}

	const { error } = await supabase.from('groups').delete().eq('id', groupId);
	if (error) return new Response(JSON.stringify({ error: error.message }), { status: 500 });
	return new Response(null, { status: 200 });
}

// ---------------------------------------------------------------------------
// Devices
// ---------------------------------------------------------------------------

export async function getDeviceApi(id: string, type: string, _token: string) {
	if (!(await ensureAuthenticated())) return null;

	const table = type === 'client' ? 'client_devices' : 'server_devices';
	const { data, error } = await supabase.from(table).select('*').eq('id', id).single();
	if (error) return null;
	return data;
}

export async function listAllDevices(_token: string): Promise<Response> {
	if (!(await ensureAuthenticated())) {
		return new Response(JSON.stringify({ error: 'Not authenticated' }), { status: 401 });
	}

	const [{ data: clientDevices }, { data: serverDevices }] = await Promise.all([
		supabase.from('client_devices').select('*'),
		supabase.from('server_devices').select('*')
	]);

	return new Response(
		JSON.stringify({ clientDevices: clientDevices ?? [], serverDevices: serverDevices ?? [] }),
		{ status: 200 }
	);
}

export async function createDeviceApi(
	deviceType: 'client' | 'server',
	body: { name: string; assignedGroupId: string },
	_token: string
): Promise<Response> {
	if (!(await ensureAuthenticated())) {
		return new Response(JSON.stringify({ error: 'Not authenticated' }), { status: 401 });
	}

	const table = deviceType === 'client' ? 'client_devices' : 'server_devices';
	const {
		data: { user }
	} = await supabase.auth.getUser();

	if (!user) {
		return new Response(JSON.stringify({ error: 'Not authenticated' }), { status: 401 });
	}

	const { data, error } = await supabase
		.from(table)
		.insert({
			name: body.name,
			assigned_group_id: body.assignedGroupId,
			assigned_user_id: user.id,
			messages: [],
			device_commands: [],
			settings: {},
			aliases: []
		})
		.select()
		.single();

	if (error) return new Response(JSON.stringify({ error: error.message }), { status: 500 });
	return new Response(JSON.stringify(data), { status: 200 });
}

export async function updateDeviceApi(
	device: Device,
	_token: string,
	thisDeviceId?: string
): Promise<Response> {
	if (!(await ensureAuthenticated())) {
		return new Response(JSON.stringify({ error: 'Not authenticated' }), { status: 401 });
	}

	const specificDevice = deviceToSpecificDevice(device);
	const type = device.type === 'client' ? 'client' : 'server';
	const table = type === 'client' ? 'client_devices' : 'server_devices';

	const { error } = await supabase.from(table).update(specificDevice).eq('id', device.id!);
	if (!error && device.id === thisDeviceId) {
		await setStore('device', specificDevice);
		await setStore('deviceType', type);
	}
	return error
		? new Response(JSON.stringify({ error: error.message }), { status: 500 })
		: new Response(null, { status: 200 });
}

export async function deleteDeviceApi(
	deviceId: string,
	deviceType: 'client' | 'server',
	_token: string
): Promise<Response> {
	if (!(await ensureAuthenticated())) {
		return new Response(JSON.stringify({ error: 'Not authenticated' }), { status: 401 });
	}

	const table = deviceType === 'client' ? 'client_devices' : 'server_devices';
	const { error } = await supabase.from(table).delete().eq('id', deviceId);
	if (error) return new Response(JSON.stringify({ error: error.message }), { status: 500 });
	return new Response(null, { status: 200 });
}

export async function addDeviceToGroupApi(
	body: { groupId: string; deviceId: string; deviceType: string },
	_token: string
): Promise<Response> {
	if (!(await ensureAuthenticated())) {
		return new Response(JSON.stringify({ error: 'Not authenticated' }), { status: 401 });
	}

	const { data: group, error: fetchError } = await supabase
		.from('groups')
		.select('devices')
		.eq('id', body.groupId)
		.single();

	if (fetchError) {
		return new Response(JSON.stringify({ error: fetchError.message }), { status: 500 });
	}

	const devices = group.devices ?? { client: [], server: [] };
	const key = body.deviceType === 'client' ? 'client' : 'server';
	if (!devices[key].includes(body.deviceId)) {
		devices[key] = [...devices[key], body.deviceId];
	}

	const { error } = await supabase.from('groups').update({ devices }).eq('id', body.groupId);
	if (error) return new Response(JSON.stringify({ error: error.message }), { status: 500 });
	return new Response(null, { status: 200 });
}

// ---------------------------------------------------------------------------
// Messages
// ---------------------------------------------------------------------------

export async function deleteMessageApi(id: string, _token: string): Promise<boolean> {
	if (!(await ensureAuthenticated())) return false;

	const { error } = await supabase.from('messages').delete().eq('id', id);
	return !error;
}

// ---------------------------------------------------------------------------
// Device session
// ---------------------------------------------------------------------------

export async function refreshDeviceSessionApi(_body: {
	user: PublicUser;
	device: unknown;
}): Promise<Response> {
	if (!(await ensureAuthenticated())) {
		return new Response(JSON.stringify({ error: 'Not authenticated' }), { status: 401 });
	}

	const { data } = await supabase.auth.getSession();
	return new Response(
		JSON.stringify({ refreshToken: data.session?.refresh_token ?? '' }),
		{ status: 200 }
	);
}
