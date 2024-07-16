import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
	// const { headers } = event.request;
	// const cookies = parse(headers.get('cookie') ?? '');
	const cookies = event.cookies;
	if (cookies.get('refreshToken')) {
		// Remove Bearer prefix
		const refreshToken = cookies.get('refreshToken');
		const response = await fetch('https://spark-api.fly.dev/session/refresh', {
			method: 'GET',
			headers: {
				'x-refresh': refreshToken
			} as HeadersInit
		});
		const accessToken = (await response.json()).accessToken;
		event.locals.accessToken = accessToken;
		const res = await fetch('https://spark-api.fly.dev/session/user', {
			headers: {
				authorization: `Bearer ${accessToken}`
			}
		});
		const user = (await res.json()).user;
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
