import type { Device } from '$lib';
import { writable } from 'svelte/store';

function createWritableStore<T>(initial: T) {
	const { subscribe, set } = writable(initial);
	return {
		subscribe,
		set: (n: T) => set(n),
		reset: () => set(initial)
	};
}

export const deviceData = createWritableStore({} as Device);
export const navOpen = createWritableStore(true);
