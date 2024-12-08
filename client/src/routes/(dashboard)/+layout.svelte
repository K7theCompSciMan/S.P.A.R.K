<script lang="ts">
	import { invoke } from '@tauri-apps/api/tauri';
	import { page } from '$app/stores';
	import NavButton from '$lib/NavButton.svelte';
	import '../../app.css';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { getStore, setStore } from '$lib/tauri';
	import type { Device, PublicUser } from '$lib';
	import type { Group } from '$lib/xata';
	import { currentUrl, navOpen } from '$lib/stores';
	let device: Device = { id: '', name: '' };
	let deviceType: string = 'client';
	let accessToken: string = '';
	let groups: Group[] = [];
	let user: PublicUser;
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
			{ name: `This Device (${device.name})`, url: `/${device.id}` },
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
	let screenWidth: number = 0;
	let navWidth = 'w-[10%]';
</script>

<svelte:window bind:innerWidth={screenWidth} />

{#await device}
	<p>Loading</p>
{:then device}
	<div class="overflow-auto h-screen w-screen bg-dark-background-800 flex">
		<nav
			class="pt-[0.5%] h-full {navWidth} border-r pt-[2%] border-slate-800 bg-dark-background-800 resize-x overflow-x-hidden sticky transition-all duration-150 md:shrink-0 lg:shrink-0 {$navOpen
				? `absolute`
				: ``}"
			style="resize: x"
		>
			<div class="relative w-auto h-fit flex flex-col justify-center text-start text-dark-text">
				{#each pages as page, i}
					<NavButton
						name={i === 0 ? (device.name ? device.name : 'This Device') : page.name}
						url={page.url}
						classModifier={`${i == 0 ? 'mt-[3%]' : ''} text-nowrap`}
						type={deviceType}
						selected={$currentUrl === page.url}
						onclick={() => {
							currentUrl.set(page.url);
							goto(page.url);
						}}
					/>
				{/each}
				<p
					class="pt-[20%] pl-[5%] text-md pb-[5%] transition-all duration-200 overflow-hidden text-nowrap {navOpen
						? 'opacity-100'
						: 'opacity-0'}"
				>
					Your Groups
				</p>
				{#each groups as group}
					<NavButton
						name={group.name}
						url={`/group/${group.id}`}
						type="group"
						classModifier={`${navOpen ? 'opacity-100' : 'opacity-0'} transition-all duration-200`}
						selected={false}
					/>
				{/each}
			</div>
			<button
				class="w-fit h-fit {$navOpen
					? 'right-[2%]'
					: 'right-[25%] rotate-180'} text-dark-primary absolute transition-all duration-200  top-[0.5%] hover:text-dark-accent hover:shadow-lg"
				on:click={() => {
					navOpen.set(!$navOpen);
					navWidth = (navWidth === 'w-[10%]') ? 'w-[2.5%] px-2' : 'w-[10%]';
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
						d="m18.75 4.5-7.5 7.5 7.5 7.5m-6-15L5.25 12l7.5 7.5"
					/>
				</svg>
			</button>
		</nav>

		<slot />
	</div>
{/await}
