<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { getStore } from '$lib/tauri';
	import { fetchGroupById } from '$lib/api';
	import type { Group } from '$lib/xata';

	let loading = true;
	let group: Group | null = null;
	let error: string | null = null;

	onMount(async () => {
		const id = $page.params.id;
		const token = (await getStore('accessToken')) as string;
		const res = await fetchGroupById(id, token);
		if (res.ok) {
			group = await res.json();
		} else {
			error = await res.text();
		}
		loading = false;
	});
</script>

<div class="min-h-screen p-6 lg:p-10 max-w-3xl">
	<button
		type="button"
		class="text-sm text-dark-accent hover:underline mb-6"
		on:click={() => goto('/dashboard')}
	>
		← Dashboard
	</button>

	{#if loading}
		<div class="space-y-4 animate-pulse" aria-busy="true">
			<div class="h-10 bg-white/5 rounded w-1/2"></div>
			<div class="h-32 spark-card"></div>
		</div>
	{:else if error}
		<p class="text-red-400">Could not load group: {error}</p>
	{:else if group}
		<h1 class="text-3xl font-bold text-white mb-2">{group.name}</h1>
		<p class="text-gray-500 text-sm font-mono mb-8">{group.id}</p>
		<div class="spark-card p-6 space-y-2 text-gray-300">
			<p>
				<span class="text-gray-500">Clients:</span>
				{group.devices?.client?.length ?? 0}
			</p>
			<p>
				<span class="text-gray-500">Servers:</span>
				{group.devices?.server?.length ?? 0}
			</p>
		</div>
	{/if}
</div>
