import type { LayoutServerLoad } from './$types';

// get `locals.user` and pass it to the `page` store
export const load: LayoutServerLoad = async ({ locals }) => {
	if(locals.user) {
		return {
			user: locals.user
		};
	}
	return {
		user: null
	};
};
