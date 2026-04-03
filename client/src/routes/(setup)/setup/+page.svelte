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
	<title>Welcome to S.P.A.R.K</title>
</svelte:head>

<div class="flex flex-col items-center text-center gap-8">
	<h1 class="text-4xl md:text-5xl font-black text-dark-primary tracking-tight">
		Welcome to <span class="text-dark-accent">S.P.A.R.K</span>
	</h1>
	<p class="text-lg text-gray-400 max-w-2xl leading-relaxed">
		The next steps help you set up a group or add this device to an existing group. You can create an
		account or sign in
		<span class="text-dark-accent font-medium">(no email required)</span>.
	</p>
	<div class="flex gap-6 items-center justify-center w-full max-w-md">
		<button
			type="button"
			class="spark-card spark-card-hover px-6 py-3 rounded-xl text-dark-text flex-1"
			disabled
			aria-disabled="true"
		>
			<span class="text-gray-500 text-sm">Back (start here)</span>
		</button>
		<button
			type="button"
			class="spark-btn-primary px-6 py-3 rounded-xl flex-1"
			on:click={() => goto('/login')}
		>
			Continue
		</button>
	</div>
</div>
