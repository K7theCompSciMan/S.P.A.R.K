<script lang="ts">
	import { invoke } from '@tauri-apps/api/tauri';
	import type { Device, Command } from '$lib';
	import { onMount } from 'svelte';
	import type { Group } from './xata';
	import { getStore } from './tauri';
	export let device: Device = {};
	export let newCommand: Command = { name: '', command: '', aliases: [''] };
	export let updateCommand: () => Promise<void> = async () => {};
	export let visible: boolean = false;
	export let location: string = '';
	export let type: 'Create' | 'Edit' = 'Create';
	let presetDropdown = false;
	let group: Group = {};
	let presets: { group: Command[]; default: Command[] } = {
		group: group.commandPresets,
		default: [
			{
				name: 'Launch Notepad',
				aliases: ['Open Notepad', 'Start Notepad'],
				command: 'start notepad'
			},
			{ name: 'Open Chrome', aliases: ['Start Chrome'], command: 'start chrome' }
		]
	};
	let selectedPreset: Command = { name: 'Choose Preset', command: '', aliases: [''] };
	onMount(async () => {
		group = (await getStore('group')) as Group;
	});
	async function runCommand(command: Command) {
		invoke('run_command', { command: command.command });
	}
	// $: console.log(newCommand);
</script>

<div
	class="bg-dark-background-300 rounded-2xl w-[80%] h-[80%] top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 absolute items-center text-dark-text {location} {visible
		? ''
		: 'hidden'}"
>
	<h1 class="text-dark-primary text-2xl text-center mt-2 mb-2">{type} Command for {device.name}</h1>
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="h-[94.3%] w-full flex flex-col">
		<div class="w-full h-[10%] flex flex-col items-center p-2 justify-center">
			<button
				class=" rounded-md text-xl w-1/4 h-full text-dark-primary bg-dark-background-500 shadow-xl hover:text-dark-accent transition-all duration-200"
				on:click={() => {
					presetDropdown = !presetDropdown;
				}}>{selectedPreset.name}</button
			>
		</div>
		<div class="w-full h-[90%] flex flex-row items-center justify-center relative">
			<div
				class="w-1/2 h-full flex flex-col items-center justify-center {presetDropdown
					? 'blur-md'
					: ''} "
			>
				<div class="flex flex-col h-1/2 w-full p-[2%]" id="name">
					<label for="name" class="text-xl">Command Name</label>
					<input
						type="text"
						bind:value={newCommand.name}
						class="bg-transparent focus:outline-none text-xl border-b w-[80%] border-dark-secondary pl-2"
					/>
				</div>
				<div class="flex flex-col h-1/2 w-full p-[2%]" id="aliases">
					<label for="name" class="text-xl">Command Aliases</label>
					<div class="flex flex-col h-full w-full">
						{#each newCommand.aliases as alias}
							<div class="mt-2 relative">
								<input
									type="text"
									bind:value={alias}
									class="bg-transparent focus:outline-none text-xl border-b border-dark-secondary pl-2"
								/>
								<button
									class="absolute left-[30%] top-[0.5%] transition-all hover:text-dark-fail duration-200"
									on:click={() =>
										(newCommand.aliases = newCommand.aliases.filter((a) => a !== alias))}
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
								newCommand.aliases = [...newCommand.aliases, ''];
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
				</div>
			</div>
			<div
				class="w-1/2 h-full flex flex-col relative items-center justify-center {presetDropdown
					? 'blur-md'
					: ''} "
			>
				<div class="flex flex-col items-center justify-center h-fit w-fit relative">
					<label for="name" class="text-xl">Command</label>
					<textarea
						name="command"
						bind:value={newCommand.command}
						class="bg-transparent rounded-2xl focus:outline-none resize-none overflow-auto no-scrollbar text-xl border w-[80%] mb-[28.5%] border-dark-secondary pl-2"
						rows="5"
						cols="50"
					>
						<code>
						{newCommand.command}
						</code>
					</textarea>
					<button
						on:click={async () => await runCommand(newCommand)}
						class="absolute right-[12%] top-[0.5%] transition hover:text-green-500"
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
								d="M15.59 14.37a6 6 0 0 1-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 0 0 6.16-12.12A14.98 14.98 0 0 0 9.631 8.41m5.96 5.96a14.926 14.926 0 0 1-5.841 2.58m-.119-8.54a6 6 0 0 0-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 0 0-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 0 1-2.448-2.448 14.9 14.9 0 0 1 .06-.312m-2.24 2.39a4.493 4.493 0 0 0-1.757 4.306 4.493 4.493 0 0 0 4.306-1.758M16.5 9a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0Z"
							/>
						</svg>
					</button>
				</div>
			</div>
			<div
				id="presets"
				class="absolute w-full h-full rounded-b-2xl opacity-75 bg-dark-background-500 flex flex-col items-center overflow-auto no-scrollbar {presetDropdown
					? ''
					: 'hidden'}"
			>
				<h1 class="text-dark-primary text-xl">Group Presets</h1>
				<div class="w-full flex-flex-col items-center justify-center">
					{#each presets.group as preset}
						<button
							class="w-[60%] ml-[20%] h-fit text-dark-text text-xl flex flex-row rounded-md bg-dark-background-300 hover:text-dark-accent transition-all duration-200 mt-2"
							on:click={() => {
								newCommand = preset;
								selectedPreset = preset;
								presetDropdown = false;
							}}
						>
							<div class="w-1/2 h-full text-start px-2">
								<h1 class="text-lg">{preset.name}</h1>
								{#each preset.aliases as alias, i}
									{#if i < 3}
										<span class="text-dark-secondary text-sm"
											>{i !== preset.aliases.length - 1 ? alias + ', ' : alias}</span
										>
									{:else if i === 3}
										<span class="text-dark-secondary text-sm">...</span>
									{/if}
								{/each}
							</div>
							<div class="w-1/2 h-full text-end px-2">
								<h1><code>{preset.command}</code></h1>
							</div>
						</button>
					{/each}
				</div>
				<h1 class="text-dark-primary text-xl mt-2 {presets.group ? '' : 'mt-[30%]'}">
					Default Presets
				</h1>
				<div class="w-full flex-flex-col items-center justify-center">
					{#each presets.default as preset}
						<button
							class="w-[60%] ml-[20%] h-fit text-dark-text text-xl flex flex-row rounded-md bg-dark-background-300 hover:text-dark-accent transition-all duration-200 mt-2"
							on:click={() => {
								newCommand = preset;
								selectedPreset = preset;
								presetDropdown = false;
							}}
						>
							<div class="w-1/2 h-full text-start px-2">
								<h1 class="text-lg">{preset.name}</h1>
								{#each preset.aliases as alias, i}
									{#if i < 3}
										<span class="text-dark-secondary text-sm"
											>{i !== preset.aliases.length - 1 ? alias + ', ' : alias}</span
										>
									{:else if i === 3}
										<span class="text-dark-secondary text-sm">...</span>
									{/if}
								{/each}
							</div>
							<div class="w-1/2 h-full text-end px-2">
								<h1><code>{preset.command}</code></h1>
							</div>
						</button>
					{/each}
				</div>
			</div>
		</div>
		<button
			class="absolute w-[20%] h-[5%] bottom-[5%] text-xl left-[40%] bg-dark-background-600 rounded-2xl hover:text-dark-success {presetDropdown
				? 'blur-md -z-10'
				: ''}"
			on:click={async () => await updateCommand()}>Save Command</button
		>
	</div>
	<button
		class="absolute top-[2%] right-[1%] hover:text-red-500 transition-all"
		on:click={() => {
			visible = false;
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
			<path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
		</svg>
	</button>
</div>
