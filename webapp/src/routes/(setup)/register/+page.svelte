<script lang="ts">
	import { onMount } from 'svelte';
	import AnimatedInputLabel from '$lib/AnimatedInputLabel.svelte';

	import { goto } from "$app/navigation";
	import { enhance } from '$app/forms';
	import { page } from '$app/stores';
	import { getStore, setStore } from '$lib/tauri';
	import { deviceData } from '$lib/stores';
	import type { Device, PublicUser } from '$lib';
    let disabled: boolean = true;
    let username: string = "";
    let password: string = "";
    let confirmPassword: string = "";

    onMount(async () => {
        let user = await getStore("user") as PublicUser;
        let device = await getStore("device") as Device;
        if(device.id  && device.assignedUser){
            goto("/dashboard");
        }
    })

    async function handleSubmit(){
        if (password !== confirmPassword) {
            alert("Passwords do not match");
            return false;
        }
        const response = await fetch('https://spark-api.fly.dev/register', {
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
        const { user, accessToken, refreshToken} = await response.json();
        await setStore("user", user);
        await setStore("accessToken", accessToken);
        await setStore("refreshToken", refreshToken);
        disabled = false;
        return true;
    }
</script>
<svelte:head>
    <title>Sign Up • SPARK</title>
</svelte:head>
<div class="text-center h-1/2 top-1/4 relative w-1/2 left-1/4 flex flex-col justify-items-center text-amber-600">
    <h1 class="text-6xl mt-[4%]">
        Sign Up to S.P.A.R.K <br>
    </h1>
    <span class="text-xl">(or <a href="/register" class='underline text-rose-700'>create an account)</a></span>
    <div class="flex justify-center ">
        <div  class="flex flex-col w-1/2 left-1/4 justify-center" >
            <AnimatedInputLabel name="Username" labelbg="bg-[#175093]" bind:value={username} size="scale-110"></AnimatedInputLabel>
            <AnimatedInputLabel name="Password" type="password" labelbg="bg-[#174f93]" bind:value={password} size="scale-110"></AnimatedInputLabel>
            <AnimatedInputLabel name="Confirm Password" type="password" labelbg="bg-[#174f93]" bind:value={confirmPassword} size="scale-110"></AnimatedInputLabel>
            <button type="submit" on:click={async() => await handleSubmit()} class="border bg-transparent w-[75%] relative left-[12.5%] pl-4 pr-4 text-current rounded-md mt-[4%] scale-110 mt[6%]">Log In</button>
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