import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async (event) => {
    if(event.locals.user){
        const res = await fetch(`https://spark-api.fly.dev/groups/${event.locals.user.id}`, {
            method: 'GET',
            headers: {
                authorization: `Bearer ${event.locals.accessToken}`
            }
        });
        if(res.status === 200){
            return {
                groups: await res.json()
            }
        }
        else {
            return {
                groups: [],
                error: await res.json()
            }
        }
    } else {
        throw redirect(301, '/login');
    }
}