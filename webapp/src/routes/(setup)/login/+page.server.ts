import type { PageServerLoad, Actions } from './$types';
import { redirect, fail } from '@sveltejs/kit';

export const load: PageServerLoad = (event) => {
	const user = event.locals.user;
	if (user) {
		throw redirect(302, '/dashboard');
	}
};

export const actions: Actions = {
	default: async (event) => {
		const formData = Object.fromEntries(await event.request.formData());

		if (!formData.email || !formData.password) {
			return fail(400, {
				error: 'Missing email or password'
			});
		}

		const { email, password } = formData as { email: string; password: string };

		const response = await fetch('https://spark-api.fly.dev/login', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ email, password })
		});
		if (response.status !== 200) {
			return fail(401, {
				response
			});
		}
		const data = await response.json();
		const { user, accessToken, refreshToken } = data;
		
		event.locals.user = user;
        event.locals.accessToken = accessToken;

		
		
		// Set the cookie
		event.cookies.set('refreshToken', refreshToken, {
			httpOnly: true,
			path: '/',
			secure: true,
			sameSite: 'strict',
			maxAge: 60 * 60 * 24 // 1 day
		});

		throw redirect(302, '/dashboard');
	}
};
