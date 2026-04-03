import type { Handle } from '@sveltejs/kit';
import { sessionRefreshApi, sessionUserApi } from '$lib/api';

export const handle: Handle = async ({ event, resolve }) => {
	const cookies = event.cookies;
	if (cookies.get('refreshToken')) {
		const refreshToken = cookies.get('refreshToken');
		const response = await sessionRefreshApi(refreshToken!);
		const data = await response.json();
		const accessToken = data.accessToken;
		const device = data.device;
		event.locals.accessToken = accessToken;
		event.locals.device = device;
		const res = await sessionUserApi(accessToken);
		const user = await res.json();
		if (res.status === 200) {
			event.locals.user = user;
		}
	} else {
		event.locals.user = null;
		event.locals.accessToken = '';
	}
	return await resolve(event);
};
