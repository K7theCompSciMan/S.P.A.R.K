<script lang="ts">
	import { goto } from '$app/navigation';
	import AnimatedInputLabel from '$lib/AnimatedInputLabel.svelte';
	import Radio from '$lib/Radio.svelte';
	import { deviceData } from '$lib/stores';
	import { onMount } from 'svelte';
	import { getStore, setStore } from '$lib/tauri';
	import type { Device, PublicUser } from '$lib';
	import type { ClientDevice, ServerDevice } from '$lib/xata';
	import {
		addDeviceToGroupApi,
		createDeviceApi,
		deleteDeviceApi,
		listAllDevices,
		refreshDeviceSessionApi
	} from '$lib/api';
	import { getRequiredAccessToken, isPublicUserReady } from '$lib/storeAccess';

	let accessToken: string;
	let devices: Device[] = [];
	let user: PublicUser;
	let loadingDevices = true;

	function assignedGroupId(): string {
		const ag = $deviceData.assignedGroup;
		if (!ag) return '';
		return typeof ag === 'string' ? ag : ag.id;
	}

	onMount(async () => {
		const u = await getStore('user');
		if (!isPublicUserReady(u)) {
			await goto('/login');
			return;
		}
		user = u;
		const token = await getRequiredAccessToken('/login');
		if (!token) return;
		accessToken = token;

		const device = await getStore('device') as Device;
		if (device.id && device.assignedUser) {
			await goto('/dashboard');
			return;
		}
		if (!assignedGroupId()) {
			await goto('/groups-select');
			return;
		}
		devices = await getDevicesInGroup();
		loadingDevices = false;
	});

	let value: string = '';
	let options = [
		{ value: 'client', label: 'Client' },
		{ value: 'server', label: 'Server' }
	];
	let deviceType: string;
	let selectedDevice: Device | null = null;

	async function getDevicesInGroup() {
		const res = await listAllDevices(accessToken);
		if (!res.ok) {
			return [];
		}
		const data = await res.json();
		let list = data.clientDevices.map((device: ClientDevice) => {
			return { ...device, type: 'client' as const };
		});
		list.push(
			...data.serverDevices.map((device: ServerDevice) => {
				return { ...device, type: 'server' as const };
			})
		);
		const gid = assignedGroupId();
		return list.filter((device: Device) => device.assignedGroup!.id === gid);
	}

	async function handleSubmit() {
		if (!deviceType || !value || (deviceType !== 'client' && deviceType !== 'server')) {
			alert('Please fill in all fields');
			return false;
		}
		const gid = assignedGroupId();
		const res = await createDeviceApi(deviceType as 'client' | 'server', { name: value, assignedGroupId: gid }, accessToken);
		if (!res.ok) {
			return { error: await res.text() };
		}
		const data = await res.json();
		const response = await addDeviceToGroupApi(
			{ groupId: gid, deviceId: data.id, deviceType },
			accessToken
		);
		if (!response.ok) {
			await deleteDeviceApi(data.id, deviceType as 'client' | 'server', accessToken);
			return false;
		}
		const refreshTokenResponse = await refreshDeviceSessionApi({ user, device: data });
		const refreshToken = (await refreshTokenResponse.json()).refreshToken;

		await setStore('refreshToken', refreshToken);
		await setStore('device', data);
		await setStore('deviceType', deviceType);
		deviceData.set({
			assignedGroup: $deviceData.assignedGroup,
			assignedUser: $deviceData.assignedUser,
			...data
		});
		await goto('/dashboard');
		return true;
	}

	async function handleConfirmDevice() {
		if (selectedDevice) {
			const t = selectedDevice.type === 'server' ? 'server' : 'client';
			deviceData.set({
				assignedGroup: $deviceData.assignedGroup,
				assignedUser: $deviceData.assignedUser,
				...selectedDevice
			});
			await setStore('device', selectedDevice);
			await setStore('deviceType', t);
			await goto('/dashboard');
		}
	}
</script>

<svelte:head>
	<title>Setup Device</title>
</svelte:head>

<div class="flex flex-col gap-8 w-full">
	<h1 class="text-3xl font-bold text-dark-primary text-center">Set up your device</h1>

	{#if loadingDevices}
		<div class="grid md:grid-cols-2 gap-6">
			<div class="space-y-4">
				<div class="h-12 rounded-lg bg-dark-background-600 animate-pulse"></div>
				<div class="h-24 rounded-lg bg-dark-background-600 animate-pulse"></div>
				<div class="h-10 rounded-lg bg-dark-background-600 animate-pulse w-1/2"></div>
			</div>
			<div class="h-64 rounded-xl bg-dark-background-600 animate-pulse"></div>
		</div>
	{:else}
		<div class="grid md:grid-cols-2 gap-8 items-start">
			<div class="spark-card p-6 space-y-6">
				<AnimatedInputLabel
					name="Device name"
					width="w-full"
					labelbg="bg-dark-background-600"
					bind:value
				></AnimatedInputLabel>
				<Radio legend="Device type" {options} fontSize={18} bind:userSelected={deviceType}></Radio>
				<button
					type="button"
					class="spark-btn-primary w-full py-3 rounded-xl"
					on:click={async () => await handleSubmit()}
				>
					Create device
				</button>
			</div>

			<div class="spark-card p-6 flex flex-col gap-4 max-h-[28rem]">
				<p class="text-gray-400 text-sm">Or choose an existing device in this group:</p>
				<div class="overflow-y-auto space-y-2 flex-1">
					{#each devices as device}
						<button
							type="button"
							class="w-full text-left p-4 rounded-xl border transition-all {selectedDevice === device
								? 'border-dark-accent bg-dark-background-500'
								: 'border-white/10 bg-dark-background-600/30 hover:border-dark-accent/30'}"
							on:click={() => {
								selectedDevice = selectedDevice === device ? null : device;
							}}
						>
							<span class="font-medium text-white">{device.name}</span>
							<span class="text-xs text-gray-500 float-right">
								{device.type === 'server' ? 'Server' : 'Client'}
							</span>
						</button>
					{/each}
				</div>
				<button
					type="button"
					class="spark-btn-primary py-3 rounded-xl opacity-90"
					disabled={!selectedDevice}
					on:click={async () => await handleConfirmDevice()}
				>
					Use selected device
				</button>
			</div>
		</div>
	{/if}

	<div class="flex justify-between pt-6">
		<button type="button" class="text-dark-accent text-sm hover:underline" on:click={() => goto('/groups-select')}>
			← Back
		</button>
		<button type="button" class="text-dark-accent text-sm hover:underline" on:click={() => goto('/dashboard')}>
			Skip to dashboard →
		</button>
	</div>
</div>
