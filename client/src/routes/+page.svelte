<script lang="ts">
	import { goto } from "$app/navigation";
	import type { Device, PublicUser } from "$lib";
	import { getStore } from "$lib/tauri";
	import { onMount } from "svelte";
    let user = {} as PublicUser;
    let device = {} as Device;
    onMount(async () => {
        user = await getStore("user") as PublicUser;
        device = await getStore("device") as Device;
        if(!user && device.id) {
            goto("/login");
        } else if (!device.id) {
            goto("/setup");
        } else {
            goto("/dashboard");
        }
    })
    console.log(user);
    console.log(device);
</script>

<svelte:head>
    <title>You aren't supposed to see this</title>
</svelte:head>

<div class="text-center h-1/2 top-1/4 relative w-1/2 left-1/4 flex  flex-col justify-items-center text-amber-600 bg-black-500">
    <h1 class="text-6xl mt-[4%]">
        You aren't supposed to see this!
    </h1>
    <p class="text-2xl mt-[4%]  w-[75%] left-[12.5%] relative">
        BEEP BOOP NO SEE THIS 
        <br>
        BEEP BOOP NO SEE THIS
    </p>
    <button disabled>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="gray" class="size-8 absolute bottom-1/4 left-[23%]">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>  
    </button>
    <button>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="gray" class="size-8 absolute bottom-1/4 left-[67%]">
            <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
        </svg>
    </button>
</div>