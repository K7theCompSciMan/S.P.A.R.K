<script lang="ts">
	import type { PublicUser } from '$lib';
	import AnimatedInputLabel from './AnimatedInputLabel.svelte';

	export let user: PublicUser;
	let primaryCommunicationMethodOptions = [
		{
			value: 'nats',
			text: 'NATS',
			description:
				"<p class='text-sm text-slate-500'>Use NATS, a publish/subscribe messaging system, to send messages between devices <i>(reduces API traffic)</i> <strong>RECOMMENDED</strong></p> "
		},
		{
			value: 'localhost',
			text: 'Localhost connection',
			description:
				"<p class='text-sm text-slate-500'>Use a localhost connection to send messages between devices <i>(reduces API traffic, requires devices to be on same WIFI or connection through VPN like Tailscale)</i> </p>"
		},
		{
			value: 'api',
			text: 'API Messaging',
			description:
				"<p class='text-sm text-slate-500'>Use the API to send messages between devices <i>(increases API traffic)</i> </p>"
		}
	];
</script>

<div class="bg-dark-background-500 w-[25%] h-[25%] rounded-2xl text-dark-text p-[1%] px-[2%]">
	<h1 class="text-xl text-dark-secondary text-center">User Settings</h1>
	<AnimatedInputLabel
		name="Username"
		labelbg="bg-dark-background-500"
		bind:value={user.username}
		size="scale-110"
	/>
	<div class="relative mt-4">
		<label for="select" class="absolute text-md bg-dark-background-500 -left-2 z-10"
			>Primary Communication Method</label
		>
		<select
			bind:value={user.settings.primaryCommunicationMethod}
			class="w-[75%] px-2 py-1 bg-transparent focus:outline-none border scale-110 rounded-2xl mt-4"
			placeholder="Select an option"
		>
			{#each primaryCommunicationMethodOptions as option}
				<option
					value={option.value}
					class="bg-dark-background-500 text-dark-text hover:text-dark-accent transition-all duration-200"
				>
					{option.text}
				</option>
			{/each}
		</select>
		<button class="absolute text-dark-text right-[10%] top-[30%] hover:text-dark-accent peer">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				fill="none"
				viewBox="0 0 24 24"
				stroke-width="1.5"
				stroke="currentColor"
				class="size-8"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z"
				/>
			</svg>
		</button>
        <div id="tooltip" class="hidden absolute bg-dark-background-500 rounded-2xl p-2 peer-hover:block  w-[100%] text-wrap hover:block -top-[100%] -right-[90%] text-sm ">
            <p>The Primary Communication Method determines the primary method in which the devices in all of your groups interact with each other and send messages with each other</p>
            <ul>
                <li><span class="font-bold text-dark-accent">NATS</span> uses a publish/subscribe messaging system to send messages between devices <i>(reduces API traffic)</i> <strong>RECOMMENDED</strong></li>
                <li><span class="font-bold text-dark-accent">Localhost connection</span> uses a localhost connection to send messages between devices <i>(reduces API traffic, <strong>requires devices to be on same WIFI or connection through VPN like Tailscale</strong>)</i></li>
                <li><span class="font-bold text-dark-accent">API Messaging</span> uses the API to send messages between devices <i>(increases API traffic)</i></li>
            </ul>
        </div>
	</div>
	<!-- tooltip here -->
</div>
