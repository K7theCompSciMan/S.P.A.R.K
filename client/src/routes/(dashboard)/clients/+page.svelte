<script lang="ts">
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
</script>

<div class="bg-slate-500 w-[80vw] ml-[5%] rounded-[2rem] shadow-2xl h-screen overflow-auto">
	<div class="flex flex-col items-center h-full pt-[3%]">
		<h1 class="text-2xl text-slate-200">Client Devices in {group.name}</h1>
		<div id="clients" class="w-1/2 h-full pt-[2%]">
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
					<div class="absolute right-[1%] top-[50%] ">
						<p id="messages" class="text-current">Messages: {client.messages.length}</p>
						<p id="messages" class="text-current">Commands: {client.deviceCommands.length}</p>
					</div>
					<button class="absolute top-[2%] right-[1%] hover:text-green-500 transition" on:click={() => goto(`/clients/${client.id}`)}>
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
	</div>
</div>
