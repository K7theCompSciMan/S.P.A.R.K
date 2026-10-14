<script lang="ts">
	import { goto } from '$app/navigation';
	import type { Device, PublicUser } from '$lib';
	import { getStore } from '$lib/tauri';
	import { onMount } from 'svelte';
	import { isDeviceReady, isPublicUserReady } from '$lib/storeAccess';
	import { restoreAuthFromStore } from '$lib/auth';

	let loading = true;

	onMount(async () => {
		await restoreAuthFromStore();
		const user = await getStore('user');
		const device = await getStore('device');
		const hasUser = isPublicUserReady(user);
		const hasDevice = isDeviceReady(device);
		if (!hasUser && hasDevice) {
			await goto('/login');
		} else if (!hasDevice) {
			await goto('/setup');
		} else {
			await goto('/dashboard');
		}
		loading = false;
	});
</script>

<svelte:head>
	<title>SPARK</title>
</svelte:head>

<div
	class="min-h-screen flex flex-col items-center justify-center bg-dark-background-900 text-dark-text px-6"
>
	{#if loading}
		<div class="flex flex-col items-center gap-4" aria-busy="true" aria-label="Loading">
			<div
				class="h-12 w-12 rounded-full border-2 border-dark-accent border-t-transparent animate-spin"
			></div>
			<p class="text-sm text-gray-500">Starting SPARK…</p>
		</div>
	{/if}
</div>
