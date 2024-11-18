<script lang="ts">
	import { goto } from "$app/navigation";
	import AnimatedInputLabel from "$lib/AnimatedInputLabel.svelte";
	import Radio from "$lib/Radio.svelte";
	import { deviceData } from "$lib/stores";
	import { onMount } from "svelte";
	import { getStore, setStore } from "$lib/tauri";
	import type { Device, PublicUser } from "$lib";
    let accessToken: string;
    let user: PublicUser;
    onMount(async () => {
        user = await getStore("user") as PublicUser;
        accessToken = await getStore("accessToken") as string;
        if(!(user.id && user.username)) {
            goto("/login");
        }
        let device = await getStore("device") as Device;
        if(device.id  && device.assignedUser){
            goto("/dashboard");
        }
        if(!device.assignedGroup){
            goto("/groups");
        }
    })
    let disabled=true;
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
        
    
    async function handleSubmit(){
        if(!deviceType || !value){
            alert("Please fill in all fields");
            return false;
        }
        const res = await fetch(`https://spark-api.fly.dev/device/${deviceType}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				authorization: `Bearer ${accessToken}`
			},
			body: JSON.stringify({ name: value, assignedGroupId: $deviceData.assignedGroup })
		});
		if (!res.ok) {
			console.log('Device creation failed');
			console.log(await res.text());
			return {
				error: await res.text()
			};
		}
		const data = await res.json();
		const response = await fetch(`https://spark-api.fly.dev/group/addDevice`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				authorization: `Bearer ${accessToken}`
			},
			body: JSON.stringify({ groupId: $deviceData.assignedGroup, deviceId: data.id, deviceType })
		});
        if(!response.ok){
            console.log('Failed to add device to group, deleting device');
			console.log(await response.text());
			await fetch(`https://spark-api.fly.dev/device/${data.id}`, {
				method: 'DELETE',
				headers: {
					'Content-Type': 'application/json',
					authorization: `Bearer ${accessToken}`
				}
			});
            return false;
        }
		const refreshTokenResponse = await fetch(`https://spark-api.fly.dev/session/device`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				authorization: `Bearer ${accessToken}`
			},
			body: JSON.stringify({ user, device: data })
		});

		const refreshToken = (await refreshTokenResponse.json()).refreshToken;
        
        await setStore("refreshToken", refreshToken);
        await setStore("device", data);
        await setStore("deviceType", deviceType);
        console.log("Device created");
        console.log(await getStore("device"));
        deviceData.set({assignedGroup: $deviceData.assignedGroup, assignedUser: $deviceData.assignedUser, ...data});
        goto("/dashboard");
        return true;
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
        <div>
            <AnimatedInputLabel name="Device Name" width="w-[40%]" labelbg="bg-[#175094]" bind:value></AnimatedInputLabel>
            <Radio  legend="Select a device type" {options} fontSize={20} bind:userSelected={deviceType} ></Radio>
            <button type="submit" on:click={async() => await handleSubmit()} class="border bg-transparent w-[75%] relative left-[12.5%] pl-4 pr-4 text-current rounded-md mt-[4%] scale-110 mt[6%]">Log In</button>
        </div>
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