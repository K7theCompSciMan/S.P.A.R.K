import { cookieStore } from '$lib/tauri';
import type { Handle } from '@sveltejs/kit';
export const handle: Handle = async ({ event, resolve }) => {
	// const { headers } = event.request;
	// const cookies = parse(headers.get('cookie') ?? '');
	const cookies = event.cookies;
	if (cookies.get('refreshToken')) {
		// Remove Bearer prefix
		let refreshToken = cookies.get('refreshToken');
		if(!refreshToken) {
			refreshToken = await cookieStore.get('refreshToken') as string;
		}
		const response = await fetch('https://spark-api.fly.dev/session/refresh', {
			method: 'GET',
			headers: {
				'x-refresh': refreshToken
			} as HeadersInit
		});
		const data = await response.json()
		const accessToken = data.accessToken;
		const device = data.device;
		event.locals.accessToken = accessToken;
		event.locals.device = device;
		const res = await fetch('https://spark-api.fly.dev/session/user', {
			headers: {
				authorization: `Bearer ${accessToken}`
			}
		});
		const user = (await res.json());
		if (res.status === 200) {
			event.locals.user = user;
		}

	}
	else {
		event.locals.user = null;
		event.locals.accessToken = "";
	}
	return await resolve(event);
};
