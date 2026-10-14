// See https://kit.svelte.dev/docs/types#app
import type { Device, PublicUser } from '$lib';

declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			accessToken: string;
			user: PublicUser | null;
			device: Device | null;
		}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};