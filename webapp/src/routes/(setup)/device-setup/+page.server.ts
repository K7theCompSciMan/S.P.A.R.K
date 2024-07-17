import { redirect, type Actions } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { deviceData } from '$lib/stores';

export const load:PageServerLoad = async (event) => {
    if(!event.locals.user) {
        return redirect(301, '/login');
    }
}

export const actions:Actions = {
    default: async (event) => {
        const formData = Object.fromEntries(await event.request.formData());
        if (!formData.name || !formData.deviceType || !formData.assignedGroupId) {
            console.log('Missing device data');
            console.log(formData);
            return {
                missing: true
            }
        }

        const { name, deviceType, assignedGroupId } = formData as { name: string, deviceType: string, assignedGroupId: string };
        const res = await fetch(`https://spark-api.fly.dev/device/${deviceType}`, {
            method: "POST",
            headers:{
                "Content-Type": 'application/json',
                authorization: `Bearer ${event.locals.accessToken}`,
            },
            body: JSON.stringify({name, assignedGroupId}),
        });
        if(!res.ok){
            console.log('Device creation failed');
            console.log(await res.text())
            return {
                error: await res.text()
            }
        }
        const data = await res.json();
        return {
            success: true,
            device: data
        }
    }
}