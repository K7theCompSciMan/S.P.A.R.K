<script lang="ts">
	import { deviceData } from '$lib/stores';
	import AnimatedInputLabel from '$lib/AnimatedInputLabel.svelte';

	import { goto } from "$app/navigation";
	import { getStore, setStore,  } from "$lib/tauri";
	import { onMount } from 'svelte';
	import type { Device, PublicUser } from '$lib';
    let disabled: boolean = true;
    let username: string = "";
    let password: string = "";
    let refreshToken: string = "";
    let user: PublicUser;

    $: if(user && user.id && user.username) {
        disabled=false;
    }

    onMount(async () => {
        user = await getStore("user") as PublicUser;
        let device = await getStore("device") as Device;
        if(device.id  && device.assignedUser){
            goto("/dashboard");
        }
        if(user && user.id && user.username){ 
            goto("/group-info");
        }
    })

    async function handleSubmit(){
        console.log("logging In")
        const response = await fetch('https://spark-api.fly.dev/login', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ username, password })
		});
		if (response.status !== 200) {
			console.log('Login Failed');
            return false;
		}
		const data = await response.json();
		const { user, accessToken, refreshToken } = data;
        console.log("setting store")
        await setStore("user", user);
        await setStore("accessToken", accessToken);
        await setStore("refreshToken", refreshToken);
        console.log("success")
        disabled = false;
        return true;
    }

    let peek = false;
</script>
<svelte:head>
    <title>Log in • SPARK</title>
</svelte:head>
<div class="text-center h-1/2 top-1/4 relative w-1/2 left-1/4 flex flex-col justify-items-center text-amber-600">
    <h1 class="text-6xl mt-[4%]">
        Log In to S.P.A.R.K <br>
    </h1>
    <span class="text-xl">(or <a href="/register" class='underline text-rose-700'>create an account)</a></span>
    <div class="flex justify-center">
        <div class="flex flex-col w-1/2 left-1/4 justify-center">
            <AnimatedInputLabel name="Username" labelbg="bg-[#175093]" bind:value={username} size="scale-110"></AnimatedInputLabel>
            <AnimatedInputLabel name="Password" type={peek ? "text": "password"} labelbg="bg-[#174f93]" bind:value={password} size="scale-110"></AnimatedInputLabel>
            <button class="absolute right-[31%] top-[42%] " on:click={() => {if(!peek) peek=true; else peek=false}}>
                {#if !peek}
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" />
                </svg>
                {:else}
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                </svg>
                {/if}                
            </button>
            <input type="text" bind:value={username} class="hidden" name="username">
            <input type="password" bind:value={password} class="hidden" name="password">
            <button on:click={async() => await handleSubmit()} class="border bg-transparent w-[75%] relative left-[12.5%] pl-4 pr-4 text-current rounded-md mt-[4%] scale-110 mt[6%]">Log In</button>
        </div>
    </div>
    <button on:click={() =>  goto("/setup")}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-8 absolute bottom-1/4 left-[23%]">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>  
    </button>
    <button on:click={() =>  goto("/group-info")} {disabled}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke={disabled ? "gray": "currentColor"} class="size-8 absolute bottom-1/4 left-[67%]">
            <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
        </svg>
    </button>
</div>