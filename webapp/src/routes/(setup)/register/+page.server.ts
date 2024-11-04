import { fail, redirect } from "@sveltejs/kit";
import type { Actions, PageServerLoad } from "./$types";

export const load: PageServerLoad = async (event) => {
	if(event.locals.user) {
		redirect(300, '/groups');
	}
} 

export const actions: Actions = {
	default: async (event) => {
		const formData = Object.fromEntries(await event.request.formData());
		if (!formData.username || !formData.password || !formData.confirmPassword) {
            console.log('Missing username or password');
			return fail(400, {
				missing: true
			});
		}

		const { username, password, confirmPassword } = formData as { username: string; password: string, confirmPassword: string };

		if(password !== confirmPassword){
			console.log('Passwords do not match');
			return fail(400, {
				passwordsMatch: false
			});
		}
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
			maxAge: 60 * 60 * 24 // 1 day
		});
        return {
            user
        }
	}
};
