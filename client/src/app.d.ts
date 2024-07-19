// See https://kit.svelte.dev/docs/types#app

import type { Device } from "$lib";
import type { User } from "$lib/xata";

// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			accessToken: string;
			user: User | null;
			device: Device | null;
		}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
