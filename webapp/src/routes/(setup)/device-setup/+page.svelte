<script lang="ts">
	import { enhance } from "$app/forms";
	import { goto } from "$app/navigation";
	import AnimatedInputLabel from "$lib/AnimatedInputLabel.svelte";
	import Radio from "$lib/Radio.svelte";
	import { deviceData } from "$lib/stores";
	import { onMount } from "svelte";
	import type { ActionData } from "./$types";
	import { page } from "$app/stores";

    let disabled=true;
    function handleContinue () {
        
    }
    let value: string = "";
    let options = [{
		value: 'client',
		label: 'Client',
	}, {
		value: 'server',
		label: 'Server',
	}
    ]
    let deviceType: string;
    export let form: ActionData;
    $: console.log($deviceData)
    $: if(form?.success && form?.device){
        deviceData.set({assignedGroup: $deviceData.assignedGroup, assignedUser: $deviceData.assignedUser, ...form.device});
        disabled = false;
    }
</script>

<svelte:head>
    <title>Setup Device</title>
</svelte:head>

<div class="text-center h-1/2 top-1/4 relative   w-1/2 left-1/4 flex  flex-col justify-items-center text-amber-600 ">
    <h1 class="text-6xl mt-[4%] text-center ">
        Set up your device 
    </h1>
    <div class="overflow-none relative  flex flex-col justify-center  mt-[1%]">
        <form method="post" use:enhance>
            <AnimatedInputLabel name="Device Name" width="w-[40%]" labelbg="bg-[#175094]" bind:value></AnimatedInputLabel>
            <Radio  legend="Select a device type" {options} fontSize={20} bind:userSelected={deviceType} ></Radio>
            <input type="text" bind:value={value} class="hidden" name="name">
            <input type="text" bind:value={deviceType} class="hidden" name="deviceType">
            <input type="text" name="assignedGroupId" class="hidden" value={$deviceData.assignedGroup}>
            <button type="submit" class="border bg-transparent w-[75%] relative left-[12.5%] pl-4 pr-4 text-current rounded-md mt-[4%] scale-110 mt[6%]">Log In</button>
        </form>
    </div>
    <button on:click={() =>  goto("/device-info")}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-8 absolute bottom-0 left-[23%]">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>  
    </button>
    <button on:click={() =>  goto("/dashboard")} {disabled}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke={disabled ? "gray" : "currentColor"} class="size-8 absolute bottom-0 left-[67%]">
            <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
        </svg>
    </button>
</div>