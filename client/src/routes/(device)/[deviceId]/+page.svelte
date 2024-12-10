<script lang="ts">
	import { invoke } from '@tauri-apps/api/tauri';
	import Radio from '$lib/Radio.svelte';
	import { goto } from '$app/navigation';
	import type { Command, Device } from '$lib';
	import { getStore, setStore } from '$lib/tauri';
	import type { ClientDevice, User, Group } from '$lib/xata';
	import { onMount } from 'svelte';
	let thisDevice: Device = {};
	let user: User = {};
	let group: Group = {};
	let accessToken = '';
	onMount(async () => {
		thisDevice = (await getStore('device')) as Device;
		user = (await getStore('user')) as User;
		group = (await getStore('group')) as Group;
		accessToken = (await getStore('accessToken')) as string;
		if (!thisDevice || !user || !group || !accessToken) {
			console.error('Missing data');
			goto('/setup');
		}
	});
</script>

<div class="w-[100%] h-[100%] text-dark-text rounded-2xl relative " style="padding: 5%;">
    <div class="w-full h-full bg-dark-background-600 rounded-2xl ">
        <h1 class="text-center text-dark-primary text-2xl pt-[4%]">Data for <span class="text-dark-accent">{thisDevice.name}</span></h1>
    </div>
</div>
