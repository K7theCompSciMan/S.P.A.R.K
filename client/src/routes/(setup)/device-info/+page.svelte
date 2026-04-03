<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	onMount(() => {
		goto('/device-setup');
	});
</script>

<svelte:head>
	<title>Device setup</title>
</svelte:head>

<div class="flex flex-col items-center justify-center min-h-[40vh] gap-4 text-gray-500 text-sm">
	<p>Redirecting to device setup…</p>
</div>
