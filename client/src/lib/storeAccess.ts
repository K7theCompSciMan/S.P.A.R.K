import { goto } from '$app/navigation';
import type { Device, PublicUser } from '$lib';
import type { Group } from '$lib/xata';
import { getStore } from './tauri';

export function isPublicUserReady(u: unknown): u is PublicUser {
	return (
		!!u &&
		typeof u === 'object' &&
		'id' in u &&
		'username' in u &&
		typeof (u as PublicUser).id === 'string' &&
		!!(u as PublicUser).id &&
		typeof (u as PublicUser).username === 'string' &&
		!!(u as PublicUser).username
	);
}

export function isDeviceReady(d: unknown): d is Device {
	return (
		!!d &&
		typeof d === 'object' &&
		'id' in d &&
		typeof (d as Device).id === 'string' &&
		!!(d as Device).id
	);
}

export function isGroupReady(g: unknown): g is Group {
	return (
		!!g &&
		typeof g === 'object' &&
		'name' in g &&
		'devices' in g &&
		!!(g as Group).devices
	);
}

export async function getRequiredStore<T>(
	key: string,
	isValid: (v: unknown) => v is T,
	fallbackRoute: string
): Promise<T | null> {
	const value = await getStore(key);
	if (!isValid(value)) {
		await goto(fallbackRoute);
		return null;
	}
	return value;
}

export async function getRequiredAccessToken(fallbackRoute: string): Promise<string | null> {
	const token = await getStore('accessToken');
	if (typeof token !== 'string' || !token) {
		await goto(fallbackRoute);
		return null;
	}
	return token;
}
