<script lang="ts">
	import type { Group } from '$lib/xata';
	import { goto } from '$app/navigation';
	import type { Command, Device, PublicUser } from '$lib';
	import { getStore, setStore } from '$lib/tauri';
	import { onMount } from 'svelte';
	import { invoke } from '@tauri-apps/api/tauri';

	let user: PublicUser = { id: '', username: '' };
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
<div class="bg-slate-500 w-[80vw] ml-[5%] rounded-[2rem] shadow-2xl h-screen overflow-auto">
	<div class="flex flex-col items-center h-full pt-[3%]">
		<h1 class="text-2xl text-slate-200">{device.name} Commands</h1>
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div id="commands" class="w-1/2 h-full pt-[2%]">
			{#each deviceCommands! as command}
				<div
					class="bg-slate-600 rounded-2xl w-full h-[10%] flex flex-row relative items-center text-slate-200 mb-[2%]"
				>
					<div class="flex flex-col h-full w-[50%]">
						<p class="relative left-[5%] top-[4%] text-xl">Command Alias</p>
						<input
							type="text"
							bind:value={command.alias}
							class="text-ellipsis border-b bg-transparent mt-[3%] w-[40%] ml-[5%] focus:outline-none"
							on:focusout={async () => await updateCommands()}
						/>
					</div>
					<code class="w-[50%] bg-slate-700 rounded-r-2xl h-full text-ellipsis">
						<p class="relative w-fit h-fit text-xl ml-[4%]">Command</p>
						<textarea
							rows="1"
							cols="50"
							bind:value={command.command}
							class="bg-slate-800 rounded-br-2xl w-full relative pt-[1%] pl-[4%] h-[70%] text-md focus:outline-none cursor-text no-scrollbar resize-none overflow-auto"
							on:focusout={async () => await updateCommands()}
						></textarea>
					</code>
					<button on:click={async () => await deleteCommand(command)}>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							stroke-width="1.5"
							stroke="currentColor"
							class="size-6 absolute right-[1%] top-[5%] transition hover:stroke-red-600"
						>
							<path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
						</svg>
					</button>
					<button on:click={async () => await runCommand(command)}>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
							stroke-width="1.5"
							stroke="currentColor"
							class="size-6 absolute right-[5%] top-[5%] transition hover:stroke-green-500"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M15.59 14.37a6 6 0 0 1-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 0 0 6.16-12.12A14.98 14.98 0 0 0 9.631 8.41m5.96 5.96a14.926 14.926 0 0 1-5.841 2.58m-.119-8.54a6 6 0 0 0-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 0 0-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 0 1-2.448-2.448 14.9 14.9 0 0 1 .06-.312m-2.24 2.39a4.493 4.493 0 0 0-1.757 4.306 4.493 4.493 0 0 0 4.306-1.758M16.5 9a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0Z"
							/>
						</svg>
					</button>
				</div>
			{/each}
			<!-- svelte-ignore a11y_click_events_have_key_events -->
			<div
				class=" bg-transparant mt-[2%] h-[5%] w-full relative flex align-middle text-slate-200 rounded-xl cursor-pointer group {createCommandPopup
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
					class="size-6 absolute top-[35%] group-hover:rotate-45 group-hover:stroke-green-500 transition-all group-hover:scale-110 duration-100 delay-75"
				>
					<path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
				</svg>
				<h2
					class="text-xl w-[80%] h-fit text-ellipsis overflow-auto text-left absolute top-[32%] left-[3.5%] group-hover:text-green-500 transition-all group-hover:scale-110 group-hover:left-[7.5%] duration-100 delay-75"
				>
					Create a New Command
				</h2>
			</div>
			<div
				class="bg-slate-600 rounded-2xl w-full h-[10%] flex items-center text-slate-200 {createCommandPopup
					? ''
					: 'hidden'} "
			>
				<div class="flex flex-col h-full w-[50%]">
					<p class="relative left-[5%] top-[4%] text-xl">New Command Alias</p>
					<input
						type="text"
						bind:value={newCommand.alias}
						class="text-ellipsis border-b bg-transparent mt-[3%] w-[40%] ml-[5%] focus:outline-none"
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
				<code class="w-[50%] bg-slate-700 rounded-r-2xl h-full text-ellipsis">
					<p class="relative w-fit h-fit text-xl ml-[4%]">New Command</p>
					<textarea
						rows="1"
						cols="50"
						bind:value={newCommand.command}
						class="bg-slate-800 rounded-br-2xl w-full relative pt-[1%] pl-[4%] h-[70%] text-md focus:outline-none cursor-text no-scrollbar resize-none overflow-auto"
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
