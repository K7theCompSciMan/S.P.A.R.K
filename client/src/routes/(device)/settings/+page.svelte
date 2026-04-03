<script lang="ts">
	import ApplicationSettings from '$lib/ApplicationSettings.svelte';
	import UserSettings from '$lib/UserSettings.svelte';

	import { onMount } from 'svelte';
	import { getStore, setStore } from '$lib/tauri';
	import type { Device, PublicUser } from '$lib';
	import { goto } from '$app/navigation';
	import { updateUserApi } from '$lib/api';
	import { getRequiredAccessToken, isPublicUserReady } from '$lib/storeAccess';

	let user: PublicUser = {
		username: 'default',
		id: '1',
		settings: { primaryCommunicationMethod: 'nats' }
	};
	let device: Device = { id: '1', name: 'default' };
	let accessToken: string = '';

	onMount(async () => {
		const u = await getStore('user');
		if (!isPublicUserReady(u)) {
			await goto('/login');
			return;
		}
		user = u;
		device = (await getStore('device')) as Device;
		const token = await getRequiredAccessToken('/login');
		if (token) accessToken = token;
	});

	const saveUser = async () => {
		const res = await updateUserApi(user, accessToken);
		return res.ok;
	};

	const saveSettings = async () => {
		await setStore('user', user);
		await saveUser();
	};
</script>

<div
	class="bg-dark-background-600 w-[80vw] ml-[5%] rounded-[2rem] shadow-2xl min-h-screen overflow-auto relative px-[1%] pt-[0.5%] flex flex-col"
>
	<div class="w-full flex-1">
		<h1 class="text-2xl text-dark-primary mt-[0.5%] w-full text-center">Settings</h1>
		<UserSettings bind:user />

		<ApplicationSettings />
	</div>
	<div class="flex justify-center py-8">
		<button
			class="flex text-dark-text rounded-xl bg-dark-primary px-6 py-2 justify-center items-center gap-2 scale-[1.2] hover:bg-dark-accent hover:scale-[1.25] hover:text-dark-success transition-all duration-200"
			on:click={saveSettings}
		>
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
					d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0 1 11.186 0Z"
				/>
			</svg>
			Save
		</button>
	</div>
</div>
