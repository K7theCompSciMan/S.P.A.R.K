<script lang="ts">
	import ApplicationSettings from '$lib/ApplicationSettings.svelte';
	import UserSettings from '$lib/UserSettings.svelte';

	import { onMount } from 'svelte';
	import { getStore, setStore } from '$lib/tauri';
	import type { Device, PublicUser } from '$lib';
	import { goto } from '$app/navigation';
	let user: PublicUser = { username: 'default', id: '1' };
	let device: Device = { id: '1', name: 'default', };
	let settings: { [key: string]: any } = {"usingNATS": false}
	onMount(async () => {
		user = (await getStore('user')) as PublicUser;
		device = (await getStore('device')) as Device;
		if (!user) {
			goto('/login');
		}
	});
	$: console.log(user);
	const saveUser = async() => {
		let res = await fetch(`https://spark-api.fly.dev/user/${user.id}`, {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(user)
		});
		if(res.ok){
			return true
		}
		return false;
	}
	const saveSettings = async() => {
		console.log('Saving settings');
		await setStore('user', user);
		for(const key in settings){
			await setStore(key, settings[key]);
		}
		await saveUser();
	}
</script>

<div
	class="bg-dark-background-600 w-[80vw] ml-[5%] rounded-[2rem] shadow-2xl h-screen overflow-auto relative px-[1%] pt-[0.5%]"
>
	<div class="w-full h-[90%]">
		<h1 class="text-2xl text-dark-primary mt-[0.5%] w-full text-center">Settings</h1>
		<UserSettings bind:user />

		<ApplicationSettings />
	</div>
	<button
		class=" flex text-dark-text rounded-xl bg-dark-primary w-[5%] relative left-[47.5%] px-2 py-1 justify-center items-center mt-[2%] scale-[1.20] mt[6%] hover:bg-dark-accent hover:scale-[1.25] hover:text-dark-success transition-all duration-200"
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
