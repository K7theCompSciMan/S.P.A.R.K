import type { Device } from '$lib';
import { writable } from 'svelte/store';

function createDeviceData() {
	const { subscribe, set } = writable({} as Device);

	return {
		subscribe,
		set: (n: Device) => set(n),
		reset: () => set({})
	};
}

function createUrlStore() {
	const { subscribe, set } = writable('' as string);
	return {
		subscribe,
		set: (n: string) => set(n),
		reset: () => set('')
	};
}

export const deviceData = createDeviceData();
export const currentUrl = createUrlStore();