import type { Device } from '$lib';
import {  writable } from 'svelte/store';

function createDeviceData() {
	const { subscribe, set } = writable({} as Device);

	return {
		subscribe,
		set: (n: Device) => set(n),
		reset: () => set({}),
	};
}

export const deviceData = createDeviceData();