// See https://kit.svelte.dev/docs/types#app

import type { PublicUser } from "$lib";

// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			accessToken: string;
			user: PublicUser | null;
		}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
