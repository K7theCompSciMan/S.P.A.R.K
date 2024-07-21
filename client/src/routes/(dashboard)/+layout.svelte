<script lang="ts">
	import NavButton from '$lib/NavButton.svelte';
	import '../../app.css';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { getStore, setStore } from '$lib/tauri';
	import type { Device, PublicUser } from '$lib';
	import type { Group } from '$lib/xata';
	let device: Device = { id: '', name: '' };
	let deviceType: string = 'client';
	let accessToken: string = '';
	let groups: Group[] = [];
	let user: PublicUser;
	onMount(async () => {
		device = (await getStore('device')) as Device;
		user = (await getStore('user')) as PublicUser;
		if (!device.id && user) {
			goto('/device-info');
		}
		if (!user) {
			goto('/setup');
		}
		deviceType = (await getStore('deviceType')) as string;

		accessToken = (await getStore('accessToken')) as string;
		const res = await fetch(`https://spark-api.fly.dev/groups/${user.id}`, {
			method: 'GET',
			headers: {
				authorization: `Bearer ${accessToken}`
			}
		});
		if (res.status === 200) {
			groups = await res.json();
		} else {
			console.error(await res.text());
		}
	});
	let pages: Page[] = [
		{ name: 'This Device', url: `/${device.id}/details` },
		{ name: 'Dashboard', url: '/dashboard' },
		{ name: 'Clients', url: '/clients' },
		{ name: 'Servers', url: '/servers' },
		{ name: 'Commands', url: '/commands' },
		{ name: 'Settings', url: '/settings' }
	];
	type Page = {
		name: string;
		url: string;
	};
</script>

<div class="overflow-auto h-screen w-screen bg-slate-600 flex">
	<nav class="pt-[0.5%] h-full w-[10%] border-r-[0.5rem] border-slate-800 bg-slate-800">
		<div class="relative w-full h-fit flex flex-col justify-center text-start text-slate-400">
			{#each pages as page, i}
				<NavButton
					name={page.name}
					url={page.url}
					classModifier={i == 0 ? 'mt-[3%]' : ''}
					type={deviceType}
				/>
			{/each}
			<p class="pt-[20%] pl-[5%] text-md pb-[5%]">Your Groups</p>
			{#each groups as group, i}
				<NavButton name={group.name} url={`/${group.id}/details`} type="group" {group} />
			{/each}
		</div>
	</nav>
	<slot />
</div>
