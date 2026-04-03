<script lang="ts">
	import { goto } from '$app/navigation';
	import type { Device, PublicUser } from '$lib';
	import { deviceData } from '$lib/stores';
	import { getStore, setStore } from '$lib/tauri';
	import type { Group } from '$lib/xata';
	import { onMount } from 'svelte';
	import { createGroupApi, deleteGroupApi, fetchUserGroups } from '$lib/api';
	import { getRequiredAccessToken, isPublicUserReady } from '$lib/storeAccess';

	let groups: Group[] = [];
	let loadingGroups = true;
	let disabled = true;
	let selectedGroup: Group | null = null;
	$: disabled = selectedGroup === null;
	let value = '';
	let user: PublicUser;
	let accessToken: string;

	onMount(async () => {
		const u = await getStore('user');
		if (!isPublicUserReady(u)) {
			await goto('/login');
			return;
		}
		user = u;
		const device = await getStore('device') as Device;
		if (device.id && device.assignedUser) {
			await goto('/dashboard');
			return;
		}

		const token = await getRequiredAccessToken('/login');
		if (!token) return;
		accessToken = token;

		const res = await fetchUserGroups(user.id, accessToken);
		if (res.status === 200) {
			groups = await res.json();
		}
		loadingGroups = false;
	});

	async function handleContinue() {
		if (selectedGroup) {
			deviceData.set({
				assignedGroup: { id: selectedGroup.id },
				assignedUser: { id: user.id },
				...$deviceData
			});
			await setStore('group', selectedGroup);
			await goto('/device-setup');
		}
	}

	async function deleteGroup(group: Group) {
		const res = await deleteGroupApi(group.id, accessToken);
		if (res.ok) {
			groups = groups.filter((g) => g !== group);
		}
	}

	async function handleSubmit(name: string) {
		createGroupPopup = false;
		groupCreated = true;
		value = '';
		const res = await createGroupApi(name, accessToken);
		if (res.ok) {
			const data = await res.json();
			groups = [...groups, data];
			selectedGroup = data;
		}
		groupCreated = false;
	}

	let createGroupPopup = false;
	$: createGroupPopup && !value ? document.getElementById('createGroupInput')?.focus() : null;
	let groupCreated = false;
</script>

<svelte:head>
	<title>Select Group</title>
</svelte:head>
<div class="flex flex-col gap-8 w-full">
	<h1 class="text-3xl font-bold text-dark-primary text-center">Select a group</h1>
	<div class="overflow-auto max-h-96 space-y-3 w-full">
		{#if loadingGroups}
			<div class="space-y-3">
				{#each [1, 2, 3] as _}
					<div class="h-16 rounded-xl bg-dark-background-600/50 animate-pulse"></div>
				{/each}
			</div>
		{:else}
		{#each groups as group}
			<div
				class="relative rounded-xl border transition-all cursor-pointer {selectedGroup === group
					? 'border-dark-accent bg-dark-background-600 shadow-lg'
					: 'border-white/10 bg-dark-background-600/40 hover:border-dark-accent/40'}"
			>
				<!-- svelte-ignore a11y_click_events_have_key_events -->
				<!-- svelte-ignore a11y_no_static_element_interactions -->
				<div
					class="p-4 pr-12"
					on:click={() => {
						selectedGroup = selectedGroup === group ? null : group;
					}}
				>
					<h2 class="text-lg font-semibold text-white text-left">{group.name}</h2>
					<p class="text-sm text-gray-500 text-right absolute top-4 right-12">
						{group.devices['server'].length} servers · {group.devices['client'].length} clients
					</p>
				</div>
				<button
					type="button"
					class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-red-400 transition-colors p-1"
					on:click|stopPropagation={async () => await deleteGroup(group)}
					aria-label="Delete group"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						stroke-width="1.5"
						stroke="currentColor"
						class="size-5"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79"
						/>
					</svg>
				</button>
			</div>
		{/each}
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<button
			type="button"
			class="w-full rounded-xl border border-dashed border-white/20 p-4 text-left text-dark-accent hover:border-dark-accent/50 hover:bg-dark-background-600/30 transition-all {createGroupPopup
				? 'hidden'
				: ''}"
			on:click={() => {
				createGroupPopup = true;
				setTimeout(() => document.getElementById('createGroupInput')?.focus(), 100);
			}}
		>
			+ Create a new group
		</button>
		<div
			class="rounded-xl border border-dark-accent/50 bg-dark-background-600 p-2 {createGroupPopup
				? ''
				: 'hidden'}"
		>
			<input
				type="text"
				id="createGroupInput"
				placeholder="Group name"
				class="w-full bg-transparent text-lg text-white px-2 py-2 focus:outline-none"
				bind:value
				on:keypress={async (event) => {
					if (event.key === 'Enter' && !groupCreated && value.trim()) {
						await handleSubmit(value.trim());
					}
				}}
				on:focusout={async () => {
					if (!value) {
						createGroupPopup = false;
					} else if (!groupCreated && createGroupPopup) {
						await handleSubmit(value.trim());
					}
				}}
			/>
		</div>
		{/if}
	</div>
	<div class="flex justify-between items-center gap-4 pt-4">
		<button type="button" class="text-dark-accent text-sm hover:underline" on:click={() => goto('/group-info')}>
			← Back
		</button>
		<button
			type="button"
			class="spark-btn-primary px-8 py-3 rounded-xl disabled:opacity-40"
			disabled={disabled}
			on:click={async () => await handleContinue()}
		>
			Next →
		</button>
	</div>
</div>
