<script lang="ts">
	import AnimatedInputLabel from '$lib/AnimatedInputLabel.svelte';

	import { goto } from '$app/navigation';
	import { getStore, setStore } from '$lib/tauri';
	import { onMount } from 'svelte';
	import type { Device, PublicUser } from '$lib';
	import { loginApi } from '$lib/api';
	import { isPublicUserReady } from '$lib/storeAccess';

	let canProceed = false;
	let username: string = '';
	let password: string = '';

	onMount(async () => {
		const u = await getStore('user');
		const device = await getStore('device') as Device;
		if (device.id && device.assignedUser) {
			await goto('/dashboard');
			return;
		}
		if (isPublicUserReady(u)) {
			canProceed = true;
			await goto('/group-info');
		}
	});

	async function handleSubmit() {
		const response = await loginApi(username, password);
		if (response.status !== 200) {
			return false;
		}
		const data = await response.json();
		const { user: u, accessToken, refreshToken } = data;
		await setStore('user', u);
		await setStore('accessToken', accessToken);
		await setStore('refreshToken', refreshToken);
		canProceed = true;
		return true;
	}

	let peek = false;
</script>

<svelte:head>
	<title>Log in • SPARK</title>
</svelte:head>
<div class="flex flex-col items-center text-center gap-8">
	<h1 class="text-4xl md:text-5xl font-bold text-dark-primary">Log in</h1>
	<p class="text-gray-400">
		New here?
		<a href="/register" class="underline text-dark-accent hover:text-white transition-colors">Create an account</a>
	</p>
	<div class="w-full max-w-md flex flex-col gap-4 relative">
		<AnimatedInputLabel name="Username" labelbg="bg-dark-background-600" bind:value={username} size="scale-110"
		></AnimatedInputLabel>
		<AnimatedInputLabel
			name="Password"
			type={peek ? 'text' : 'password'}
			labelbg="bg-dark-background-600"
			bind:value={password}
			size="scale-110"
		></AnimatedInputLabel>
		<button
			type="button"
			class="absolute right-2 top-[42%] text-gray-500 hover:text-dark-accent"
			on:click={() => {
				peek = !peek;
			}}
			aria-label={peek ? 'Hide password' : 'Show password'}
		>
			{#if !peek}
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
						d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88"
					/>
				</svg>
			{:else}
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
						d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z"
					/>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"
					/>
				</svg>
			{/if}
		</button>
		<button
			type="button"
			class="spark-btn-primary w-full py-3 rounded-xl mt-2"
			on:click={async () => await handleSubmit()}
		>
			Log in
		</button>
	</div>
	<div class="flex gap-6 items-center justify-center w-full max-w-md pt-4">
		<button type="button" class="text-dark-accent text-sm hover:underline" on:click={() => goto('/setup')}>
			← Back
		</button>
		<button
			type="button"
			class="text-dark-accent text-sm hover:underline disabled:opacity-40"
			disabled={!canProceed}
			on:click={() => goto('/group-info')}
		>
			Next →
		</button>
	</div>
</div>
