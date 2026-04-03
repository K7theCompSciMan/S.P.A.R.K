import { deviceToSpecificDevice, type Device, type PublicUser } from '$lib';
import { setStore } from './tauri';

export const API_BASE = 'https://spark-api.fly.dev';

export async function getDeviceApi(id: string, type: string, token: string) {
	const res = await fetch(`${API_BASE}/device/${type}/${id}`, {
		headers: { authorization: `Bearer ${token}` }
	});
	return res.ok ? await res.json() : null;
}

export async function updateDeviceApi(device: Device, token: string, thisDeviceId?: string) {
	const specificDevice = deviceToSpecificDevice(device);
	const type = device.type === 'client' ? 'client' : 'server';

	const res = await fetch(`${API_BASE}/device/${type}/`, {
		method: 'PUT',
		headers: { 'Content-Type': 'application/json', authorization: `Bearer ${token}` },
		body: JSON.stringify({ ...specificDevice, id: device.id })
	});

	if (res.ok && device.id === thisDeviceId) {
		await setStore('device', specificDevice);
		await setStore('deviceType', type);
	}
	return res;
}

export async function deleteMessageApi(id: string, token: string): Promise<boolean> {
	const res = await fetch(`${API_BASE}/device/message/${id}`, {
		method: 'DELETE',
		headers: { authorization: `Bearer ${token}` }
	});
	return res.ok;
}

export async function updateUserApi(user: PublicUser, token: string): Promise<Response> {
	return fetch(`${API_BASE}/user`, {
		method: 'PUT',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		},
		body: JSON.stringify(user)
	});
}

export async function fetchUserGroups(userId: string, token: string): Promise<Response> {
	return fetch(`${API_BASE}/groups/${userId}`, {
		headers: { authorization: `Bearer ${token}` }
	});
}

export async function fetchGroupById(groupId: string, token: string): Promise<Response> {
	return fetch(`${API_BASE}/group/${groupId}`, {
		headers: { authorization: `Bearer ${token}` }
	});
}

export async function listAllDevices(token: string): Promise<Response> {
	return fetch(`${API_BASE}/devices`, {
		headers: { authorization: `Bearer ${token}` }
	});
}

export async function createDeviceApi(
	deviceType: 'client' | 'server',
	body: { name: string; assignedGroupId: string },
	token: string
): Promise<Response> {
	return fetch(`${API_BASE}/device/${deviceType}`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		},
		body: JSON.stringify(body)
	});
}

export async function addDeviceToGroupApi(
	body: { groupId: string; deviceId: string; deviceType: string },
	token: string
): Promise<Response> {
	return fetch(`${API_BASE}/group/addDevice`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		},
		body: JSON.stringify(body)
	});
}

export async function deleteDeviceApi(
	deviceId: string,
	deviceType: 'client' | 'server',
	token: string
): Promise<Response> {
	return fetch(`${API_BASE}/device/${deviceType}/${deviceId}`, {
		method: 'DELETE',
		headers: {
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	});
}

export async function refreshDeviceSessionApi(body: {
	user: PublicUser;
	device: unknown;
}): Promise<Response> {
	return fetch(`${API_BASE}/session/device`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body)
	});
}

export async function createGroupApi(name: string, token: string): Promise<Response> {
	return fetch(`${API_BASE}/group`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		},
		body: JSON.stringify({ name })
	});
}

export async function deleteGroupApi(groupId: string, token: string): Promise<Response> {
	return fetch(`${API_BASE}/group/${groupId}`, {
		method: 'DELETE',
		headers: { authorization: `Bearer ${token}` }
	});
}

export async function loginApi(username: string, password: string): Promise<Response> {
	return fetch(`${API_BASE}/login`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ username, password })
	});
}

export async function registerApi(username: string, password: string): Promise<Response> {
	return fetch(`${API_BASE}/register`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ username, password })
	});
}

export async function sessionRefreshApi(refreshToken: string): Promise<Response> {
	return fetch(`${API_BASE}/session/refresh`, {
		method: 'GET',
		headers: { 'x-refresh': refreshToken } as HeadersInit
	});
}

export async function sessionUserApi(accessToken: string): Promise<Response> {
	return fetch(`${API_BASE}/session/user`, {
		headers: { authorization: `Bearer ${accessToken}` }
	});
}
