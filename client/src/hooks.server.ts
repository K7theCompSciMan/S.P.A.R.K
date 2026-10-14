import type { Handle } from '@sveltejs/kit';
import { sessionRefreshApi, sessionUserApi } from '$lib/api';

// NOTE: This hook runs only on the SvelteKit dev-server / SSR side.
// In the Tauri build (prerender + static adapter) it is not invoked for
// navigation — auth state is managed entirely via the Tauri store.
export const handle: Handle = async ({ event, resolve }) => {
	const cookies = event.cookies;
	const refreshToken = cookies.get('refreshToken');

	if (refreshToken) {
		try {
			const refreshResponse = await sessionRefreshApi(refreshToken);
			if (refreshResponse.ok) {
				const { accessToken } = await refreshResponse.json();
				event.locals.accessToken = accessToken;

				const userResponse = await sessionUserApi(accessToken);
				if (userResponse.ok) {
					event.locals.user = await userResponse.json();
				} else {
					event.locals.user = null;
				}
			} else {
				event.locals.user = null;
				event.locals.accessToken = '';
			}
		} catch {
			event.locals.user = null;
			event.locals.accessToken = '';
		}
	} else {
		event.locals.user = null;
		event.locals.accessToken = '';
	}

	return await resolve(event);
};