<script lang="ts">
	import type { Group } from '$lib/xata';
	import { goto } from '$app/navigation';
	import type { Command, Device, PublicUser } from '$lib';
	import { getStore, setStore } from '$lib/tauri';
	import { onMount } from 'svelte';
	import { invoke } from '@tauri-apps/api/tauri';
	import CommandCard from '$lib/CommandCard.svelte';

	let user: PublicUser = { id: '', username: '',  settings: { primaryCommunicationMethod: "nats"} };
	let group: Group = {};
	let device: Device = { deviceCommands: [] };
	let deviceType = '';
	let accessToken = '';
	onMount(async () => {
		device = (await getStore('device')) as Device;
		user = (await getStore('user')) as PublicUser;
		group = (await getStore('group')) as Group;
		deviceType = (await getStore('deviceType')) as string;
		accessToken = (await getStore('accessToken')) as string;
		if (!user) {
			goto('/login');
		}
	});
	let deviceCommands: Command[] = [];
	setTimeout(() => {
		deviceCommands = device.deviceCommands!;
	}, 100);
	async function updateCommands() {
		let response = await fetch(`https://spark-api.fly.dev/device/${deviceType}`, {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json',
				authorization: `Bearer ${accessToken}`
			},
			body: JSON.stringify({ ...device, deviceCommands })
		});
		if (response.ok) {
			console.log('Commands updated');
			await setStore('device', device);
		} else {
			console.error(await response.text());
		}
	}
	let newCommand: Command = { alias: '', command: '' };
	async function handleSubmit(newCommand: Command) {
		if (!newCommand.alias && newCommand.command) {
			console.error('Command alias is required');
			return;
		} else if (newCommand.alias && !newCommand.command) {
			console.error('Command is required');
			return;
		} else if (!newCommand.alias && !newCommand.command) {
			console.error('Command alias and command are required');
			return;
		} else {
			createCommandPopup = false;
			commandCreated = true;
			deviceCommands?.push(newCommand);
			console.log(deviceCommands);
			await updateCommands();
		}
		deviceCommands = device.deviceCommands!;
	}
	let commandCreated = false;
	let createCommandPopup = false;

	async function deleteCommand(command: Command) {
		deviceCommands = deviceCommands.filter((c) => c !== command);
		await updateCommands();
	}

	async function runCommand(command: Command) {
		invoke('run_command', { command: command.command });
	}
</script>

<!-- svelte-ignore css_unused_selector -->
<div class="bg-background-500 w-[80vw] ml-[5%] rounded-[2rem] shadow-2xl h-screen overflow-auto">
	<div class="flex flex-col items-center h-full pt-[3%]">
		<h1 class="text-2xl text-slate-200">{device.name} Commands</h1>
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div id="commands" class="w-1/2 h-full pt-[2%]">
			{#each deviceCommands as command}
				<CommandCard {command} {updateCommands} {deleteCommand} {runCommand} />
			{/each}
			<!-- svelte-ignore a11y_click_events_have_key_events -->
			<!-- svelte-ignore a11y_no_static_element_interactions -->
			<div
				class=" bg-transparant mt-[2%] h-[5%] w-full relative flex align-middle text-dark-text rounded-xl cursor-pointer group {createCommandPopup
					? 'hidden'
					: ''} "
				id="add"
				on:click={() => {
					createCommandPopup = true;
					setTimeout(() => document.getElementById('createGroupInput')?.focus(), 100);
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
			</div>
			<div
				class="bg-background-500 rounded-2xl w-[90%] relative left-[5%] h-[20%] flex items-center text-dark-text {createCommandPopup
					? ''
					: 'hidden'} "
			>
				<div class="flex flex-col h-full w-[50%] bg-dark-background-300 rounded-l-2xl">
					<p class="relative left-[5%] top-[4%] text-xl">New Command Alias</p>
					<input
						type="text"
						bind:value={newCommand.alias}
						class="text-ellipsis border-b border-dark-secondary bg-dark-background-300 mt-[3%] w-[100%] ml-[5%] focus:outline-none"
						on:focusout={async () => {
							if (!newCommand.alias) {
								createCommandPopup = false;
							} else if (!commandCreated && createCommandPopup) {
								await handleSubmit(newCommand);
							}
						}}
						on:keypress={async (event) => {
							if (event.key === 'Enter' && !commandCreated) {
								await handleSubmit(newCommand);
							}
						}}
					/>
				</div>
				<code
					class="w-[50%] bg-dark-background-500 rounded-r-2xl h-full text-ellipsis border border-dark-secondary"
				>
					<p class="relative w-fit h-fit text-xl ml-[4%]">New Command</p>
					<textarea
						rows="1"
						cols="50"
						bind:value={newCommand.command}
						class="bg-dark-background-500 rounded-br-2xl w-full relative pt-[1%] pl-[4%] h-[70%] text-md focus:outline-none cursor-text no-scrollbar resize-none overflow-auto"
						on:focusout={async () => {
							if (!newCommand.command) {
								createCommandPopup = false;
							} else if (!commandCreated && createCommandPopup) {
								await handleSubmit(newCommand);
							}
						}}
						on:keypress={async (event) => {
							if (event.key === 'Enter' && !commandCreated) {
								await handleSubmit(newCommand);
							}
						}}
					></textarea>
				</code>
			</div>
		</div>
	</div>
</div>
