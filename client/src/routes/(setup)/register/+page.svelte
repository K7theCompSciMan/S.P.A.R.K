<script lang="ts">
	import { onMount } from 'svelte';
	import AnimatedInputLabel from '$lib/AnimatedInputLabel.svelte';

	import { goto } from '$app/navigation';
	import { getStore, setStore } from '$lib/tauri';
	import type { Device } from '$lib';
	import { registerApi } from '$lib/api';

	let canProceed = false;
	let email = '';
	let username = '';
	let password = '';
	let confirmPassword = '';
	let errorMsg = '';

	onMount(async () => {
		const device = (await getStore('device')) as Device;
		if (device.id && device.assignedUser) {
			await goto('/dashboard');
		}
	});

	async function handleSubmit() {
		errorMsg = '';

		if (password !== confirmPassword) {
			errorMsg = 'Passwords do not match.';
			return false;
		}

		const response = await registerApi(email, username, password);

		if (response.status !== 200) {
			const body = await response.json().catch(() => ({}));
			errorMsg = body.error ?? 'Registration failed. Please try again.';
			return false;
		}

		const { user, accessToken, refreshToken } = await response.json();
		await setStore('user', user);
		await setStore('accessToken', accessToken);
		await setStore('refreshToken', refreshToken);
		canProceed = true;
		return true;
	}
</script>

<svelte:head>
	<title>Sign Up • SPARK</title>
</svelte:head>
<div class="flex flex-col items-center text-center gap-8">
	<h1 class="text-4xl md:text-5xl font-bold text-dark-primary">Sign up</h1>
	<p class="text-gray-400">
		Already have an account?
		<a href="/login" class="underline text-dark-accent hover:text-white transition-colors">Sign in</a>
	</p>

	{#if errorMsg}
		<div class="w-full max-w-md bg-red-500/10 border border-red-500/20 text-red-400 text-xs py-2.5 px-3 rounded-xl text-left">
			{errorMsg}
		</div>
	{/if}

	<div class="w-full max-w-md flex flex-col gap-4">
		<AnimatedInputLabel
			name="Email"
			type="email"
			labelbg="bg-dark-background-600"
			bind:value={email}
			size="scale-110"
		></AnimatedInputLabel>
		<AnimatedInputLabel
			name="Username"
			labelbg="bg-dark-background-600"
			bind:value={username}
			size="scale-110"
		></AnimatedInputLabel>
		<AnimatedInputLabel
			name="Password"
			type="password"
			labelbg="bg-dark-background-600"
			bind:value={password}
			size="scale-110"
		></AnimatedInputLabel>
		<AnimatedInputLabel
			name="Confirm Password"
			type="password"
			labelbg="bg-dark-background-600"
			bind:value={confirmPassword}
			size="scale-110"
		></AnimatedInputLabel>
		<button
			type="button"
			class="spark-btn-primary w-full py-3 rounded-xl mt-2"
			on:click={async () => await handleSubmit()}
		>
			Create account
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
