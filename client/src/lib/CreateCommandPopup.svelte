<script lang="ts">
	import type { Device, Command } from '$lib';
	export let device: Device = {};
	export let newCommand: Command = { alias: '', command: '' };
	let step = '1';
    let type = '';
</script>

<div
	class="bg-dark-background-300 rounded-2xl w-[80%] h-[80%] top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 absolute items-center text-dark-text"
>
	<h1 class="text-dark-primary text-2xl text-center mt-2 mb-2">Create Command for {device.name}</h1>
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div
		id="step1"
		class=" h-[94.3%] text-center {step === '1'
			? 'visible'
			: 'hidden'} flex flex-row justify-left items-center"
	>
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<div
			id="Application Control"
			class="w-1/2 h-full relative border-dark-secondary border-r bg-slate-600 rounded-2xl rounded-r-none hover:text-dark-accent hover:cursor-pointer transition-all duration-200 group {type==="application" ? 'text-dark-accent' : 'text-dark-secondary'}"
            on:click={() => {type = "application"; ;}}
		>
			<h1
				class=" text-5xl text-center absolute top-[47%] left-1/2 transform -translate-x-1/2 -translate-y-[50%] p-2 bg-transparent transition-all duration-200 rounded-2xl"
			>
				Application Control
			</h1>
		</div>
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<div
			id="OS Control"
			class="w-1/2 h-full relative border-dark-secondary border-l bg-slate-600 rounded-2xl rounded-l-none hover:text-dark-accent hover:cursor-pointer transition-all duration-200 group {type==="os" ? 'text-dark-accent' : 'text-dark-secondary'}"
            on:click={() => {type = "os"; ;} }
		>
			<h1
				class=" text-5xl text-center absolute top-[47%] left-1/2 transform -translate-x-1/2 -translate-y-[50%] p-2 bg-transparent transition-all duration-200 rounded-2xl"
			>
				OS Control
			</h1>
		</div>
	</div>
</div>
