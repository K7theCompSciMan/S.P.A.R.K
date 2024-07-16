import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async (event) => {
    if(event.locals.user) {
        throw redirect(300, "/dashboard");
    }
    else {
        console.log("User is not logged in");
        throw redirect(301, "/setup");
    }
}