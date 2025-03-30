<script lang="ts">
	import { goto } from "$app/navigation";
	import AnimatedInputLabel from "$lib/AnimatedInputLabel.svelte";
	import Radio from "$lib/Radio.svelte";
	import { deviceData } from "$lib/stores";
	import { onMount } from "svelte";
	import { getStore, setStore } from "$lib/tauri";
	import type { Device, PublicUser } from "$lib";
	import type { ClientDevice, ServerDevice } from "$lib/xata";
    let accessToken: string;
    let devices: Device[];
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
        if(!$deviceData.assignedGroup){
            goto("/groups-select");
        }
        devices = await getDevicesInGroup();
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
    let selectedDevice: Device | null = null;

    async function getDevicesInGroup() {
        const res = await fetch(`https://spark-api.fly.dev/devices`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                // authorization: `Bearer ${accessToken}`
            }
        }        );
        let data = await res.json();
        let devices = data.clientDevices.map((device: ClientDevice) => {
            return {...device, type: 'client'};
        });

        devices.push(...data.serverDevices.map((device: ServerDevice) => {
            return {...device, type: 'server'};
        }));
        
        console.log(devices)
        devices = devices.filter((device: Device) => device.assignedGroup!.id === $deviceData.assignedGroup!.id);
        return devices;
    }
        
    
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

    async function handleConfirmDevice() {
        if (selectedDevice) {
            deviceData.set({
                assignedGroup: $deviceData.assignedGroup,
                assignedUser: $deviceData.assignedUser,
                ...selectedDevice
            });
            await setStore('device', selectedDevice);
            goto('/dashboard');
        }
    }
</script>

<svelte:head>
    <title>Setup Device</title>
</svelte:head>

<div class="text-center h-1/2 top-1/4 relative   w-1/2 left-1/4 flex  flex-col justify-items-center text-amber-600 ">
    <h1 class="text-6xl mt-[4%] text-center ">
        Set up your device 
    </h1>
    <div class="overflow-none relative h-1/2 flex flex-row justify-center  mt-[1%]">
        <div class="flex flex-col w-1/2 h-full justify-center items-center">
            <AnimatedInputLabel name="Device Name" width="w-[40%]" labelbg="bg-[#175094]" bind:value></AnimatedInputLabel>
            <Radio  legend="Select a device type" {options} fontSize={20} bind:userSelected={deviceType} ></Radio>
            <button type="submit" on:click={async() => await handleSubmit()} class="border bg-transparent w-[40%]  pl-4 pr-4 text-current rounded-md mt-[4%] scale-110 ">Create Device</button>
        </div>
        <div class="overflow-auto w-1/2 h-full mt-[1%]">
            <p> or select a device from the list below</p>
            {#each devices as device}
                <div
                    class="border {selectedDevice === device
                        ? 'border-emerald-700 border-2 bg-gray-200 scale-105'
                        : 'bg-gray-500'}  mt-[2%] h-[12%] w-[75%] relative left-[12.5%] flex align-middle rounded-xl cursor-pointer shadow-xl hover:bg-gray-200 hover:scale-105 transition-all delay-75 duration-150"
                >
                    <!-- svelte-ignore a11y_click_events_have_key_events -->
                    <!-- svelte-ignore a11y_no_static_element_interactions -->
                    <div
                        on:click={() => {
                            if (selectedDevice === device) {
                                selectedDevice = null;
                            } else {
                                selectedDevice = device;
                            }
                        }} class="flex flex-row justify-start w-full h-full"
                    >
                        <h2
                            class="text-xl w-[80%] h-fit text-ellipsis overflow-auto text-left ml-[2%]"
                        >
                            {device.name}
                        </h2>
                        <p class="text-xl text-right ">
                            {device.type === 'server' ? 'Server' : 'Client'}
                        </p>
                    </div>
                </div>
            {/each}
            <button type="submit" on:click={async() => await handleConfirmDevice()} class="border bg-transparent w-[40%]  pl-4 pr-4 text-current rounded-md mt-[4%] scale-110 ">Confirm Device</button>
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