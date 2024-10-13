import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = (event) => {
    if (event.locals.user != null) {
        console.log("redirecting to dashboard: " + event.locals.user.username);
        throw redirect(302, '/dashboard');
    } else {
        throw redirect(302, '/setup')
    }
}