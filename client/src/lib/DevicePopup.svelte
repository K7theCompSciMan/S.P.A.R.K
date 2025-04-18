<script lang="ts">
	import { deviceToSpecificDevice, type Command, type Device } from '$lib';
	import type { Server } from '@sveltejs/kit';
	import CommandCard from './CommandCard.svelte';
	import CommandPopup from './CommandPopup.svelte';
	import Radio from './Radio.svelte';
	import { setStore } from './tauri';
	import type { ClientDevice, ServerDevice } from './xata';

	export let device: Device = {};
	export let thisDevice: Device = {};
	export let visible: boolean = false;

	let updateDevice: () => void = async() => {

		let new_device = deviceToSpecificDevice(device);
		// console.log(client);
		// console.log(device);
		if (device.type === 'client') {
			// console.log('client');
			let res = await fetch(`https://spark-api.fly.dev/device/client/`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json',
					authorization: `Bearer ${accessToken}`
				},
				body: JSON.stringify({ ...new_device as ClientDevice, id: device.id } as ClientDevice)
			});
			if (res.ok) {
				// console.log('Client updated');
				if (device.id === thisDevice.id) {
					await setStore('device', new_device);
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
				body: JSON.stringify({ ...new_device as ServerDevice, id: device.id } as ServerDevice)
			});
			if (res.ok) {
				// console.log('Device updated');
				if (device.id === thisDevice.id) {
					await setStore('device', new_device);
					await setStore('deviceType', 'server');
				}
			} else {
				console.error(await res.text());
			}
		}
	};
	let deleteCommand: (command: Command) => Promise<void> = async (command: Command) => {
		device.deviceCommands = device.deviceCommands!.filter(
			(c: Command) => c !== command
		);
		await updateDevice();
	}
;
	export let runCommand: (command: Command) => Promise<void> = async () => {};
	let getDevice: (id: string) => Promise<any> = async (id: string) => {
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
	};
	let deleteMessage: (id: string) => Promise<void> = async (id: string) => {
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
	};
	// let updateCommands: () => Promise<void> = async () => {};

	export let accessToken: string = '';

	export let createCommandPopup = false;
	export let newCommand: Command = { name: '', command: '', aliases: [''] };
	// $: console.log(device.aliases);

</script>

<div
	class=" bg-dark-background-500 rounded-2xl w-[80%] h-[80%] {visible
		? 'block'
		: 'hidden'} translate-y-[-113%] ml-[10%] shadow-2xl no-scrollbar overflow-hidden"
>
	<h1 class="text-2xl text-dark-primary mt-[0.5%] w-full text-center">
		Settings for <span class="text-bold text-dark-accent">{device.name}</span>
	</h1>
	<div class="w-full h-full flex flex-row">
		<div class = "w-1/2 h-[95%] p-2">
			<div class="w-2/3 h-1/3 text-dark-text pl-[1%] rounded-2xl pt-[0.5%]">
				<label for="name" class="text-xl">Device Name: </label>
				<input
					type="text"
					class="bg-transparent focus:outline-none text-xl border-b border-dark-secondary pl-2"
					bind:value={device.name}
				/>
				<div
					class="relative border border-dark-secondary rounded-2xl p-2 mt-2 overflow-scroll no-scrollbar w-full h-1/2"
				>
					<label for="name" class="text-xl mb-2">Device Aliases</label>
					{#each device.aliases! as alias}
						<div class="relative">
							<input
								type="text"
								class="bg-transparent focus:outline-none text-xl border-b border-dark-secondary pl-2"
								bind:value={alias}
							/>
							<button
								class="absolute left-[30%] top-[0.5%] transition-all hover:text-dark-fail duration-200"
								on:click={() => (device.aliases = device.aliases!.filter((a) => a !== alias))}
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
					{/each}
					<button
						class="bg-transparent focus:outline-none text-xl mt-[2%] w-fit h-fit border-dark-secondary"
						on:click={() => {
							device.aliases = [...(device.aliases || []), ''];
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
							<path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
						</svg>
					</button>
				</div>
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
					bind:userSelected={device.type}
				/>
			</div>
			<div
				class="overflow-auto text-dark-text w-[90%] ml-2 h-[45%] rounded-2xl relative text-center border border-dark-secondary"
			>
				<h1 class="text-2xl mb-[2%]">Device Messages:</h1>
				<div class="rounded-2xl no-scrollbar overflow-auto flex flex-col items-center w-full h-[70%]">
					{#each device.messages || [] as message}
						{#await getDevice(message.from)}
							<h1 class="text-slate-400 text-xl">Loading Messages...</h1>
						{:then device}
							<div
								class="text-lg bg-dark-background-300 mb-[2%] rounded-xl w-[80%] h-fit text-dark-text relative"
							>
								<span class="text-dark-accent cursor-pointer">{device.name}</span> sent:
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
		<div
			class="overflow-auto text-dark-text w-[45%] ml-2 h-[90%] rounded-2xl right-[5%] top-[5%] text-center border border-dark-secondary no-scrollbar"
		>
			<h1 class="text-2xl mb-[2%]">Device Commands:</h1>
			<div class="rounded-2xl no-scrollbar overflow-auto flex flex-col items-center w-full h-[85%]">
				{#each device.deviceCommands! as command}
					<CommandCard
						{command}
						updateCommands={async () => await updateDevice()}
						{deleteCommand}
						{runCommand}
					/>
				{/each}
			</div>
			<button
				class=" bg-transparant mt-[2%] h-[5%] w-full relative flex align-middle text-dark-text rounded-xl cursor-pointer group {createCommandPopup
					? 'hidden'
					: ''} "
				id="add"
				on:click={() => {
					createCommandPopup = true;
				}}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
					stroke-width="1.5"
					stroke="currentColor"
					id="add"
					class="size-6 absolute left-[8%] top-[35%] group-hover:rotate-45 group-hover:stroke-green-500 transition-all group-hover:scale-110 duration-200"
				>
					<path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
				</svg>
			</button>
		</div>
	</div>
	<button
		on:click={() => {
			visible = false;
			updateDevice();
		}}
		class="absolute text-dark-text top-[0.5%] right-[0.5%] hover:text-red-500 transition-all"
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
</div>
<CommandPopup
	location="absolute left-[50%]"
	{device}
	bind:newCommand
	bind:visible={createCommandPopup}
	updateCommand={async () => {
		createCommandPopup = false;
		if (device.deviceCommands != undefined && device.deviceCommands.length > 0) {
			device.deviceCommands = [...device.deviceCommands!, newCommand];
		} else {
			device.deviceCommands = [newCommand];
		}
		await updateDevice();
	}}
	on:close={() => {
		newCommand = { name: '', command: '', aliases: [''] };
	}}
/>
