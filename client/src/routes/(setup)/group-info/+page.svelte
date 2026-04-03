<script lang="ts">
	import { goto } from '$app/navigation';
	import type { Device, PublicUser } from '$lib';
	import { getStore } from '$lib/tauri';
	import { onMount } from 'svelte';
	import { isPublicUserReady } from '$lib/storeAccess';

	onMount(async () => {
		const user = await getStore('user');
		if (!isPublicUserReady(user)) {
			await goto('/login');
			return;
		}
		const device = await getStore('device') as Device;
		if (device.id && device.assignedUser) {
			await goto('/dashboard');
		}
	});
</script>

<svelte:head>
	<title>Group info • SPARK</title>
</svelte:head>
<div class="flex flex-col items-center text-center gap-8">
	<h1 class="text-3xl md:text-4xl font-bold text-dark-primary">Choose a group</h1>
	<p class="text-gray-400 max-w-xl leading-relaxed">
		Groups bundle the clients and servers your assistant can talk to. Next, pick an existing group or create a
		new one.
	</p>
	<div class="flex gap-6 items-center justify-center w-full max-w-md pt-4">
		<button type="button" class="text-dark-accent text-sm hover:underline" on:click={() => goto('/setup')}>
			← Back
		</button>
		<button type="button" class="spark-btn-primary px-8 py-3 rounded-xl" on:click={() => goto('/groups-select')}>
			Continue
		</button>
	</div>
</div>
