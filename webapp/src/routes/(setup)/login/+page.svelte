<script lang="ts">
	import type { ActionData } from './$types';
	import AnimatedInputLabel from '$lib/AnimatedInputLabel.svelte';

	import { goto } from "$app/navigation";
	import { enhance } from '$app/forms';
	import { page } from '$app/stores';
    let disabled: boolean = true;
    let username: string = "";
    let password: string = "";
    export let form: ActionData;
    $: if(form?.user || $page.data.user){
        disabled=false;
        // $page.data.user = form?.user;
    }
    $: console.log(form?.user, $page.data.user)

</script>
<svelte:head>
    <title>Log in • SPARK</title>
</svelte:head>
<div class="text-center h-1/2 top-1/4 relative w-1/2 left-1/4 flex flex-col justify-items-center text-amber-600">
    <h1 class="text-6xl mt-[4%]">
        Log In to S.P.A.R.K <br>
    </h1>
    <span class="text-xl">(or <a href="/register" class='underline text-rose-700'>create an account)</a></span>
    <div class="flex justify-center ">
        <form method="post" class="flex flex-col w-1/2 left-1/4 justify-center" use:enhance>
            <AnimatedInputLabel name="Username" labelbg="bg-[#175093]" bind:value={username} size="scale-110"></AnimatedInputLabel>
            <AnimatedInputLabel name="Password" type="password" labelbg="bg-[#174f93]" bind:value={password} size="scale-110"></AnimatedInputLabel>
            <input type="text" bind:value={username} class="hidden" name="username">
            <input type="password" bind:value={password} class="hidden" name="password">
            <button type="submit" class="border bg-transparent w-[75%] relative left-[12.5%] pl-4 pr-4 text-current rounded-md mt-[4%] scale-110 mt[6%]">Log In</button>
        </form>
    </div>
    <button on:click={() =>  goto("/setup")}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-8 absolute bottom-1/4 left-1/3">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>  
    </button>
    <button on:click={() =>  goto("/group-info")} {disabled}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke={disabled ? "gray": "currentColor"} class="size-8 absolute bottom-1/4 left-[67%]">
            <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
        </svg>
    </button>
</div>