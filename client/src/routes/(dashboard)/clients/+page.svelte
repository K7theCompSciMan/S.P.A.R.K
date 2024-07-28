<script lang="ts">
	import Radio from '$lib/Radio.svelte';
	import { goto } from '$app/navigation';
	import type { Device } from '$lib';
	import { getStore, setStore } from '$lib/tauri';
	import type { ClientDevice, User, Group } from '$lib/xata';
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

	async function updateClient(client: ClientDevice) {
		let res = await fetch(`https://spark-api.fly.dev/device/client/`, {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json',
				authorization: `Bearer ${accessToken}`
			},
			body: JSON.stringify({ ...client, id: client.id })
		});
		if (res.ok) {
			console.log('Client updated');
			if (client.id === thisDevice.id) {
				await setStore('device', client);
			}
		} else {
			console.error(await res.text());
		}
	}

	$: console.log(clients);

	let selectedDevice: ClientDevice = { id: '', name: '', messages: [], deviceCommands: [] };
	let selectedDeviceType = 'client';
	let settingsPopup = false;
	async function getServerDevice(id: string) {
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
	async function deleteMessage(id: string) {
		let res = await fetch(`https://spark-api.fly.dev/device/message/${id}`, {
			method: 'DELETE',
			headers: {
				'Content-Type': 'application/json',
				authorization: `Bearer ${accessToken}`
			}
		});
		if (res.ok) {
			console.log('Message deleted');
		} else {
			console.error(await res.text());
		}
	}
</script>

<div class="bg-slate-500 w-[80vw] ml-[5%] rounded-[2rem] shadow-2xl h-screen overflow-auto">
	<div class="flex flex-col items-center h-full pt-[3%]">
		<h1 class="text-2xl text-slate-200 {settingsPopup ? 'hidden' : ''}">
			Client Devices in {group.name}
		</h1>
		<div id="clients" class="w-1/2 h-full pt-[2%] {settingsPopup ? 'hidden' : ''} ">
			{#each clients as client}
				<div
					class="bg-slate-600 rounded-2xl w-full h-[12%] flex flex-row relative items-center text-slate-200 mb-[2%] cursor-pointer"
				>
					<input
						id="clientName"
						type="text"
						class="text-xl h-fit border-b-2 border-slate-800 w-[30%] pl-[1%] focus:outline-none absolute top-[8%] left-[1.5%] bg-transparent"
						placeholder="Name"
						bind:value={client.name}
						on:focusout={async () => {
							await updateClient(client);
						}}
						on:keypress={async (e) => {
							if (e.key === 'Enter') {
								await updateClient(client);
							}
						}}
					/>
					<div class="absolute right-[1%] top-[50%]">
						<p id="messages" class="text-current">Messages: {client.messages.length}</p>
						<p id="messages" class="text-current">Commands: {client.deviceCommands.length}</p>
					</div>
					<button
						class="absolute top-[2%] right-[1%] hover:text-green-500 transition-all"
						on:click={() => {
							selectedDevice = client;
							settingsPopup = true;
						}}
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							stroke-width="1.5"
							stroke="currentColor"
							class="size-6"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5"
							/>
						</svg>
					</button>
				</div>
			{/each}
		</div>
		{#if settingsPopup}
			<div class=" bg-slate-600 rounded-2xl w-[80%] h-[95%] block relative">
				<h1 class="text-2xl text-slate-200 mt-[0.5%] w-full text-center">
					Settings for {selectedDevice.name}
				</h1>
				<div class="w-1/3 h-1/3 text-slate-200 pl-[1%] rounded-2xl pt-[0.5%]">
					<label for="name" class="text-xl">Device Name: </label>
					<input
						type="text"
						class="bg-transparent focus:outline-none text-xl border-b border-black pl-2"
						bind:value={selectedDevice.name}
					/>
					<Radio
						legend="Device Type"
						options={[
							{
								value: 'client',
								label: 'Client'
							},
							{
								value: 'server',
								label: 'Server'
							}
						]}
						fontSize={20}
						bind:userSelected={selectedDeviceType}
					/>
				</div>
				<button
					on:click={() => {
						settingsPopup = false;
					}}
					class="absolute text-slate-200 top-[0.5%] right-[0.5%] hover:text-red-500 transition-all"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						stroke-width="1.5"
						stroke="currentColor"
						class="size-6"
					>
						<path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
					</svg>
				</button>
				<div
					class="overflow-auto text-slate-200 w-[45%] ml-2 h-[45%] rounded-2xl relative text-center"
				>
					<h1 class="text-2xl mb-[2%]">Device Messages:</h1>
					<div
						class="rounded-2xl no-scrollbar overflow-auto flex flex-col items-center w-full h-[90%]"
					>
						{#each selectedDevice.messages as message}
							{#await getServerDevice(message.from) then serverDevice}
								<div
									class="text-lg bg-slate-500 mb-[2%] rounded-xl w-[80%] h-fit text-slate-200 relative"
								>
									<span class="text-slate-400 cursor-pointer">{serverDevice.name}</span> sent:
									<div class="text-green-500">{message.content}</div>
									<button
										class="absolute top-[5%] right-[1%] hover:text-red-500 transition-all duration-100"
										on:click={async () => await deleteMessage(message.id)}
									>
										<svg
											xmlns="http://www.w3.org/2000/svg"
											fill="none"
											viewBox="0 0 24 24"
											stroke-width="1.5"
											stroke="currentColor"
											class="size-6"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
											/>
										</svg>
									</button>
								</div>
							{/await}
						{/each}
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>
