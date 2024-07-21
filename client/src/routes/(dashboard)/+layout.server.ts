import type { LayoutServerLoad } from './$types';

// get `locals.user` and pass it to the `page` store
export const load: LayoutServerLoad = async ({ locals }) => {
	if (locals.user) {
		if (locals.accessToken) {
			if (locals.device) {
				return {
					user: locals.user,
					accessToken: locals.accessToken,
					device: locals.device
				};
			}
			return {
				user: locals.user,
				accessToken: locals.accessToken,
				device: null
			};
		}
		return {
			user: locals.user,
			accessToken: '',
			device: null
		};
	}
	return {
		user: null,
		accessToken: '',
		device: null
	};
};
