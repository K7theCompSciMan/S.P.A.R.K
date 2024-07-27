<script lang="ts">
	import { invoke } from '@tauri-apps/api/tauri';
	import { page } from '$app/stores';
	import NavButton from '$lib/NavButton.svelte';
	import '../../app.css';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { getStore, setStore, store } from '$lib/tauri';
	import type { Device, PublicUser } from '$lib';
	import type { Group } from '$lib/xata';
	import { currentUrl } from '$lib/stores';
	let device: Device = { id: '', name: '' };
	let deviceType: string = 'client';
	let accessToken: string = '';
	let groups: Group[] = [];
	let user: PublicUser;
	let navDisplay = true;
	onMount(async () => {
		currentUrl.set(window.location.pathname);
		device = (await getStore('device')) as Device;
		user = (await getStore('user')) as PublicUser;
		if (!device.id && user) {
			goto('/device-info');
		}
		if (!user) {
			goto('/setup');
		}
		deviceType = (await getStore('deviceType')) as string;
		let response = await fetch(`https://spark-api.fly.dev/device/${deviceType}/${device.id}`, {
			method: 'GET'
		});
		if (response.ok) {
			device = await response.json();
			await setStore('device', device);
			let updateGroup = await fetch(`https://spark-api.fly.dev/group/${device.assignedGroup!.id}`, {
				method: 'GET'
			});
			if (updateGroup.ok) {
				let group = await updateGroup.json();
				await setStore('group', group);
			} else {
				console.error(await updateGroup.text());
			}
			let updateUser = await fetch(`https://spark-api.fly.dev/user/${device.assignedUser!.id}`, {
				method: 'GET'
			});
			if (updateUser.ok) {
				let user = (await updateUser.json()).user;
				await setStore('user', user);
			} else {
				console.error(await updateUser.text());
			}
		} else {
			console.error(await response.text());
		}

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
	let pages: Page[];
	setTimeout(() => {
		pages = [
			{ name: `This Device (${device.name})`, url: `/${deviceType}s/${device.id}` },
			{ name: 'Dashboard', url: '/dashboard' },
			{ name: 'Clients', url: '/clients' },
			{ name: 'Servers', url: '/servers' },
			{ name: 'Commands', url: '/commands' },
			{ name: 'Settings', url: '/settings' }
		];
	}, 100);
	type Page = {
		name: string;
		url: string;
	};
	let withClose = false;
	let screenWidth: number = 0;
	$: screenWidth < 1024 ? (navDisplay = false) : (navDisplay = true);
</script>

<svelte:window bind:innerWidth={screenWidth} />

{#await device}
	<p>Loading</p>
{:then device}
	<div class="overflow-auto h-screen w-screen bg-slate-600 flex">
		<nav
			class="pt-[0.5%] h-full w-[10%] border-r-[0.5rem] border-slate-800 bg-slate-800 min-w-36 {navDisplay
				? 'opacity-100'
				: 'hidden opacity-0'} transition-all duration-150 md:shrink-0 lg:shrink-0 {withClose
				? `absolute`
				: ``}"
		>
			<div class="relative w-full h-fit flex flex-col justify-center text-start text-slate-400">
				{#each pages as page, i}
					<NavButton
						name={i === 0 ? (device.name ? device.name : 'This Device') : page.name}
						url={page.url}
						classModifier={`${i == 0 ? 'mt-[3%]' : ''}`}
						type={deviceType}
						selected={$currentUrl === page.url}
						onclick={() => {
							currentUrl.set(page.url);
							goto(page.url);
						}}
					/>
				{/each}
				<p class="pt-[20%] pl-[5%] text-md pb-[5%]">Your Groups</p>
				{#each groups as group}
					<NavButton name={group.name} url={`/group/${group.id}`} type="group" selected={false} />
				{/each}
			</div>
			<button
				class="w-fit h-fit {withClose
					? ''
					: 'hidden'} text-slate-300 absolute -right-2 top-1 hover:text-slate-50 hover:shadow-lg"
				on:click={() => {
					withClose = false;
					navDisplay = false;
				}}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
					stroke-width="1.5"
					stroke="currentColor"
					class="size-6"
				>
					<path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
				</svg>
			</button>
		</nav>
		<button
			class="{navDisplay
				? 'hidden'
				: 'left-[2%] top-[2%]'} border h-fit w-fit mr-[2%] text-slate-300"
			on:click={() => {
				navDisplay = true;
				withClose = true;
			}}
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
					d="M10.5 6h9.75M10.5 6a1.5 1.5 0 1 1-3 0m3 0a1.5 1.5 0 1 0-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-9.75 0h9.75"
				/>
			</svg></button
		>

		<slot />
	</div>
{/await}
