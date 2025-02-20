<script lang="ts">
	import type { Group } from '$lib/xata';
	import { goto } from '$app/navigation';
	import type { Command, Device, PublicUser } from '$lib';
	import { getStore, setStore } from '$lib/tauri';
	import { onMount } from 'svelte';
	import { invoke } from '@tauri-apps/api/tauri';
	import CommandCard from '$lib/CommandCard.svelte';
	import CreateCommandPopup from '$lib/CommandPopup.svelte';

	let user: PublicUser = { id: '', username: '', settings: { primaryCommunicationMethod: 'nats' } };
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
			let new_device = await response.json();
			device = new_device;
			await setStore('device', device);
			console.log('Commands updated');
		} else {
			console.error(await response.text());
		}
	}
	let newCommand: Command = { name: '', command: '', aliases: [''] };
	async function handleSubmit(newCommand: Command) {
		if (!newCommand.name && newCommand.command) {
			console.error('Command name is required');
			return;
		} else if (newCommand.name && !newCommand.command) {
			console.error('Command is required');
			return;
		} else if (!newCommand.name && !newCommand.command) {
			console.error('Command name and command are required');
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
	let popup=false;
</script>

<!-- svelte-ignore css_unused_selector -->
<div class="bg-background-500 w-[80vw] ml-[5%] rounded-[2rem] shadow-2xl h-screen overflow-auto no-scrollbar">
	<div class="flex flex-col items-center justify-center h-full pt-[3%] relative">
		<h1 class="text-2xl text-slate-200">{device.name} Commands</h1>
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div id="commands" class="w-1/2 h-full pt-[2%]">
			<div class="rounded-2xl no-scrollbar overflow-auto flex flex-col items-center w-full max-h-[90%]">
				{#each deviceCommands as command}
					<CommandCard bind:popup={popup} {command} {updateCommands} {deleteCommand} {runCommand} />
				{/each}
			</div>
			<!-- svelte-ignore a11y_click_events_have_key_events -->
			<!-- svelte-ignore a11y_no_static_element_interactions -->
			<div
				class=" bg-transparant mt-[2%] h-[5%] w-full relative flex align-middle text-dark-text rounded-xl cursor-pointer group {createCommandPopup || popup
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
		</div>
		<CreateCommandPopup
			location="absolute left-[50%]"
			{device}
			bind:newCommand
			bind:visible={createCommandPopup}
			updateCommand={async () => {
				createCommandPopup = false;
				commandCreated = true;
				deviceCommands = [...device.deviceCommands!, newCommand];
				console.log(deviceCommands);
				await updateCommands();
			}}
		/>
	</div>
</div>
