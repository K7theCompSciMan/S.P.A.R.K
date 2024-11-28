<script lang='ts'>
	import type { PublicUser } from "$lib";
	import AnimatedInputLabel from "./AnimatedInputLabel.svelte";
	import type { User } from "./xata";
    import { compile } from 'mdsvex'

    export let user: PublicUser;
    let primaryCommunicationMethodOptions = [
        {value: 'nats', text: "NATS", description: "Use NATS, a publish/subscribe messaging system, to send messages between devices *(reduces API traffic)* **RECOMMENDED** "},
        {value: 'localhost', text: "Localhost connection", description: "Use a localhost connection to send messages between devices *(reduces API traffic, requires devices to be on same WIFI or connection through VPN like Tailscale)*"},
        {value: 'api', text: "API Messaging", description: "Use the API to send messages between devices *(increases API traffic)*"}
    ];
</script>   

<div class='bg-dark-background-500 w-[25%] h-[25%] rounded-2xl text-dark-text p-[1%] px-[2%]'>
    <h1 class="text-xl text-dark-secondary text-center">User Settings</h1>
    <AnimatedInputLabel name="Username" labelbg="bg-dark-background-500" bind:value={user.username } size="scale-110" />
    <select bind:value={user.settings.primaryCommunicationMethod}>
		{#each primaryCommunicationMethodOptions as option}
			<option value={option}>
				{option.text}
                {#await compile(option.description)}
                loading...
                {:then description}
                {@html description}
                {:catch error}
                {error}
                {/await}
			</option>
		{/each}
	</select>
</div>