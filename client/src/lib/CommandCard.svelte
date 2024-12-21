<script lang="ts">
	import type { Command } from '$lib';

	export let command: Command;
	export let updateCommands: () => Promise<void> = async () => {};
	export let deleteCommand: (command: Command) => Promise<void> = async () => {};
	export let runCommand: (command: Command) => Promise<void> = async () => {};
</script>

<div
	class="bg-dark-background-300 rounded-2xl w-[90%] ml-[5%] h-[20%] flex flex-row relative items-center text-dark-text mb-[2%]"
>
	<div class="flex flex-col h-full w-[50%] overflow-auto no-scrollbar">
		<p class="relative left-[5%] top-[4%] text-xl text-dark-accent">Command name</p>
		<input
			type="text"
			bind:value={command.name}
			class="text-ellipsis border-b bg-transparent mt-[3%] w-[80%] ml-[5%] focus:outline-none"
			on:focusout={async () => await updateCommands()}
		/>
		<p class="relative left-[5%] top-[4%] text-lg text-dark-accent">Command Aliases</p>
		<div class="flex flex-col h-full w-full ml-[5%] relative">
			{#each command.aliases as alias}
				<div class="mt-2 relative">
					<input
						type="text"
						bind:value={alias}
						class="bg-transparent focus:outline-none text-sm border-b border-dark-secondary pl-2"
					/>
					<button class="absolute right-[50%] top-[0%] transition hover:text-red-500" on:click={async() => {command.aliases.filter((a) => a !== alias); await updateCommands()}}>
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
								d="M6 18 18 6M6 6l12 12"
							/>
						</svg>
						
					</button>
				</div>
			{/each}
			<button
				class="bg-transparent focus:outline-none text-sm mt-[2%] w-fit h-fit border-dark-secondary"
				on:click={() => {
					command.aliases.push('');
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
	<code
		class="w-[50%] bg-dark-background-500 rounded-r-2xl h-full text-ellipsis border border-dark-secondary"
	>
		<p class="relative w-fit h-fit text-xl ml-[4%] top-[3%] text-dark-accent">Command</p>
		<textarea
			rows="1"
			cols="50"
			bind:value={command.command}
			class="bg-transparent rounded-br-2xl w-full relative pt-[1%] pl-[4%] h-[70%] text-md focus:outline-none cursor-text no-scrollbar resize-none overflow-auto"
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
	<button
		on:click={async () => await runCommand(command)}
		class="absolute right-[8%] top-[5%] transition hover:text-green-500"
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
