import { redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { cookieStore } from '$lib/tauri';

export const load: PageServerLoad = async (event) => {
	if (!event.locals.user) {
		return redirect(301, '/login');
	}
};

export const actions: Actions = {
	default: async (event) => {
		const formData = Object.fromEntries(await event.request.formData());
		if (!formData.name || !formData.deviceType || !formData.assignedGroupId) {
			console.log('Missing device data');
			console.log(formData);
			return {
				missing: true
			};
		}

		const { name, deviceType, assignedGroupId } = formData as {
			name: string;
			deviceType: string;
			assignedGroupId: string;
		};
		const res = await fetch(`https://spark-api.fly.dev/device/${deviceType}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				authorization: `Bearer ${event.locals.accessToken}`
			},
			body: JSON.stringify({ name, assignedGroupId })
		});
		if (!res.ok) {
			console.log('Device creation failed');
			console.log(await res.text());
			return {
				error: await res.text()
			};
		}
		const data = await res.json();
		event.locals.device = data;
		const response = await fetch(`https://spark-api.fly.dev/group/addDevice`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				authorization: `Bearer ${event.locals.accessToken}`
			},
			body: JSON.stringify({ groupId: assignedGroupId, deviceId: data.id, deviceType })
		});
		const refreshTokenResponse = await fetch(`https://spark-api.fly.dev/session/device`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				authorization: `Bearer ${event.locals.accessToken}`
			},
			body: JSON.stringify({ user: event.locals.user, device: data })
		});

		const refreshToken = (await refreshTokenResponse.json()).refreshToken;
		console.log(refreshToken);

		event.cookies.set('refreshToken', refreshToken, {
			httpOnly: true,
			path: '/',
			secure: true,
			sameSite: 'strict',
			expires: new Date(8.64e15)
		});

		await cookieStore.set('refreshToken', refreshToken);
		await cookieStore.save();

		if (response.ok) {
			return {
				success: true,
				device: data
			};
		} else {
			console.log('Failed to add device to group, deleting device');
			console.log(await response.text());
			await fetch(`https://spark-api.fly.dev/device/${data.id}`, {
				method: 'DELETE',
				headers: {
					'Content-Type': 'application/json',
					authorization: `Bearer ${event.locals.accessToken}`
				}
			});
			return {
				error: await response.text()
			};
		}
	}
};
