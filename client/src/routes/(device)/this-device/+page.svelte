<script lang="ts">
	import CreateCommandPopup from '$lib/CommandPopup.svelte';
	import { invoke } from '@tauri-apps/api/tauri';
	import Radio from '$lib/Radio.svelte';
	import { goto } from '$app/navigation';
	import type { Command, Device } from '$lib';
	import { getStore, setStore } from '$lib/tauri';
	import type { ClientDevice, User, Group, ServerDevice } from '$lib/xata';
	import { onMount } from 'svelte';
	import DevicePopup from '$lib/DevicePopup.svelte';
	let thisDevice: Device = {};
	let user: User = {};
	let group: Group = {};
	let accessToken = '';
	onMount(async () => {
		thisDevice = (await getStore('device')) as Device;
		let type = (await getStore('deviceType')) as string;
		thisDevice.type = type;
		user = (await getStore('user')) as User;
		group = (await getStore('group')) as Group;
		accessToken = (await getStore('accessToken')) as string;
		if (!thisDevice || !user || !group || !accessToken) {
			console.error('Missing data');
			goto('/setup');
		}
	});

	async function updateDevice(thisDevice: Device) {
		// console.log(client);
		// console.log(selectedDevice);
		if (thisDevice.type === 'client') {
			// console.log('client');
			let res = await fetch(`https://spark-api.fly.dev/device/client/`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json',
					authorization: `Bearer ${accessToken}`
				},
				body: JSON.stringify({ ...thisDevice as ClientDevice, id: thisDevice.id } as ClientDevice)
			});
			if (res.ok) {
				// console.log('Client updated');
				if (thisDevice.id === thisDevice.id) {
					await setStore('device', thisDevice);
					await setStore('deviceType', 'client');
				}
			} else {
				console.error(await res.text());
			}
		} else {
			// console.log('server');
			let res = await fetch(`https://spark-api.fly.dev/device/server/`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json',
					authorization: `Bearer ${accessToken}`
				},
				body: JSON.stringify({ ...thisDevice as ServerDevice, id: thisDevice.id } as ServerDevice)
			});
			if (res.ok) {
				// console.log('Device updated');
				if (thisDevice.id === thisDevice.id) {
					await setStore('device', thisDevice);
					await setStore('deviceType', 'server');
				}
			} else {
				console.error(await res.text());
			}
		}
	}
	async function deleteMessage(id: string) {
		let res = await fetch(`https://spark-api.fly.dev/device/message/${id}`, {
			method: 'DELETE',
			headers: {
				'Content-Type': 'application/json',
				authorization: `Bearer ${accessToken}`
			}
		});
		if (res.ok) {
			// console.log('Message deleted');
		} else {
			console.error(await res.text());
		}
	}
	async function deleteCommand(command: Command) {
		thisDevice.deviceCommands = thisDevice.deviceCommands!.filter(
			(c: Command) => c !== command
		);
		await updateDevice(thisDevice);
	}

	async function runCommand(command: Command) {
		invoke('run_command', { command: command.command });
	}
</script>

<div class="w-[100%] h-[100%] text-dark-text rounded-2xl relative " style="padding: 5%;">
    <div class="w-full h-full bg-dark-background-600 rounded-2xl ">
        <h1 class="text-center text-dark-primary text-2xl pt-[4%]">Data for <span class="text-dark-accent">{thisDevice.name}</span></h1>
		<DevicePopup device={thisDevice} thisDevice={thisDevice} visible={true} {runCommand} {accessToken}/>
    </div>
</div>
