<script lang="ts">
	import DevicePopup from '$lib/DevicePopup.svelte';
	import { invoke } from '@tauri-apps/api/tauri';
	import Radio from '$lib/Radio.svelte';
	import { goto } from '$app/navigation';
	import { deviceToSpecificDevice, type Command, type Device } from '$lib';
	import { getStore, setStore } from '$lib/tauri';
	import type { ClientDevice, User, Group, ServerDevice } from '$lib/xata';
	import { onMount } from 'svelte';
	let thisDevice: Device = {};
	let user: User = {};
	let clients: ClientDevice[] = [];
	let group: Group = {};
	let accessToken = '';
	onMount(async () => {
		thisDevice = (await getStore('device')) as Device;
		user = (await getStore('user')) as User;
		group = (await getStore('group')) as Group;
		accessToken = (await getStore('accessToken')) as string;
		if (!thisDevice || !user || !group || !accessToken) {
			console.error('Missing data');
			goto('/setup');
		}
		group.devices['client'].forEach(async (element: string) => {
			let res = await fetch(`https://spark-api.fly.dev/device/client/${element}`, {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json',
					authorization: `Bearer ${accessToken}`
				}
			});
			if (res.ok) {
				let data = await res.json();
				clients = [...clients, data];
			} else {
				console.error(await res.text());
			}
		});
	});
	$: console.log(selectedDevice)
	let newCommand: Command = { name: '', command: '', aliases: [''] };
	async function handleSubmit() {
		updateDevice(selectedDevice);
	}
	async function updateDevice(client: Device) {
		selectedDevice = client;
		client = deviceToSpecificDevice(client);
		// console.log(client);
		// console.log(selectedDevice);
		if (selectedDevice.type === 'client') {
			// console.log('client');
			let res = await fetch(`https://spark-api.fly.dev/device/client/`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json',
					authorization: `Bearer ${accessToken}`
				},
				body: JSON.stringify({ ...client as ClientDevice, id: client.id } as ClientDevice)
			});
			if (res.ok) {
				// console.log('Client updated');
				if (client.id === thisDevice.id) {
					await setStore('device', client);
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
				body: JSON.stringify({ ...client as ClientDevice, id: client.id } as ServerDevice)
			});
			if (res.ok) {
				// console.log('Device updated');
				if (client.id === thisDevice.id) {
					await setStore('device', client);
					await setStore('deviceType', 'server');
				}
			} else {
				console.error(await res.text());
			}
		}
	}
	
	let selectedDevice: Device = {
		id: '',
		name: '',
		messages: [],
		deviceCommands: [],
		type: 'client',
	};
	// $: console.log(selectedDevice.aliases);
	let settingsPopup = false;
	async function getDevice(id: string) {
		let res = await fetch(`https://spark-api.fly.dev/device/client/${id}`, {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
				authorization: `Bearer ${accessToken}`
			}
		});
		if (res.ok) {
			return await res.json();
		} else {
			let res = await fetch(`https://spark-api.fly.dev/device/server/${id}`, {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json',
					authorization: `Bearer ${accessToken}`
				}
			});
			if (res.ok) {
				return await res.json();
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
		selectedDevice.deviceCommands = selectedDevice.deviceCommands!.filter(
			(c: Command) => c !== command
		);
		await updateDevice(selectedDevice);
	}

	async function runCommand(command: Command) {
		invoke('run_command', { command: command.command });
	}
</script>

<div
	class="bg-dark-background-600 w-[80vw] ml-[5%] rounded-[2rem] shadow-2xl h-screen overflow-hidden no-scrollbar relative"
>
	<div class="flex flex-col items-center h-full pt-[3%]">
		<h1 class="text-2xl text-dark-primary">
			Client Devices in <span class="text-dark-accent">{group.name}</span>
		</h1>
		{#await clients}
			<h1 class="text-dark-primary text-2xl">Loading...</h1>
		{:then clients}
			<div id="clients" class="w-1/2 h-full pt-[2%] {settingsPopup ? 'hidden' : ''}">
				{#each clients as client}
					<!-- svelte-ignore a11y_click_events_have_key_events -->
					<!-- svelte-ignore a11y_no_static_element_interactions -->
					<div
						class="bg-dark-background-500 rounded-2xl w-full h-[12%] flex flex-row relative items-center text-dark-text mb-[2%] cursor-pointer hover:scale-105 shadow-lg hover:shadow-dark-accent hover:text-dark-accent transition-all duration-200"
						on:click={(e) => {
							if (e.target!.id === 'clientName') {
							} else {
								selectedDevice = client;
								selectedDevice.type = 'client';
								settingsPopup = true;
							}
						}}
					>
						<input
							id="clientName"
							type="text"
							class="text-xl h-fit border-b-2 border-dark-secondary w-[30%] pl-[1%] focus:outline-none absolute top-[8%] left-[1.5%] bg-transparent"
							placeholder="Name"
							bind:value={client.name}
							on:focusout={async () => {
								await updateDevice(client);
							}}
							on:keypress={async (e) => {
								if (e.key === 'Enter') {
									await updateDevice(client);
								}
							}}
						/>
						<div class="absolute right-[1%] top-[50%]">
							<p id="messages" class="text-current">Messages: {client.messages.length}</p>
							<p id="messages" class="text-current">Commands: {client.deviceCommands.length}</p>
						</div>
					</div>
				{/each}
			</div>
		{/await}
	</div>
	<DevicePopup
		bind:device={selectedDevice}
		bind:newCommand
		bind:visible={settingsPopup}
		{runCommand}
		{accessToken}
		{thisDevice}
		on:close={() => {
			// let client = clients.find((c) => c.id === selectedDevice.id);
			// client = deviceToSpecificDevice(selectedDevice); 
			// updateDevice(client);
			// newCommand = { name: '', command: '', aliases: [''] };
		}}
	/>
</div>
