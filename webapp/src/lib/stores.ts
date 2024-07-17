import type { Device } from '$lib';
import { get, writable } from 'svelte/store';

function createDeviceData() {
	const { subscribe, set } = writable({} as Device);

	return {
		subscribe,
		set: (n: any) => set(n),
		reset: () => set({}),
	};
}

export const deviceData = createDeviceData();