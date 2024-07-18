import { fail, redirect } from "@sveltejs/kit";
import type { Actions, PageServerLoad } from "./$types";
import { cookieStore } from "$lib/tauri";

export const load: PageServerLoad = async (event) => {
	if(event.locals.user) {
		redirect(300, '/group-info');
	}
} 

export const actions: Actions = {
	default: async (event) => {
		const formData = Object.fromEntries(await event.request.formData());
		if (!formData.username || !formData.password) {
            console.log('Missing username or password');
			return fail(400, {
				missing: true
			});
		}

		const { username, password } = formData as { username: string; password: string };

		const response = await fetch('https://spark-api.fly.dev/login', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ username, password })
		});
		if (response.status !== 200) {
			console.log('Login Failed');
			return fail(401, {
				username,
				incorrect: true
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
			expires: new Date(8.64e15)
		});
		
		await cookieStore.set('refreshToken', refreshToken);
		await cookieStore.save();
        return {
            user
        }
	}
};
