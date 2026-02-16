<script lang="ts">
    import { onMount } from 'svelte';
    import { fly } from 'svelte/transition';
    import { goto } from '$app/navigation';
    import DevicePopup from '$lib/DevicePopup.svelte';
    import { getStore, runCommand } from '$lib/tauri';
    import { getDeviceApi, updateDeviceApi } from '$lib/api';
    import type { Device } from '$lib';
    import type { ServerDevice, User, Group } from '$lib/xata';

    let loading = true;
    let user: User = {};
    let group: Group = { name: '', devices: { client: [], server: [] } };
    let servers: ServerDevice[] = [];
    let accessToken = '';
    
    let settingsPopup = false;
    let selectedDevice: Device = { id: '', name: '', type: 'server' };

    onMount(async () => {
        user = (await getStore('user')) as User;
        group = (await getStore('group')) as Group;
        accessToken = (await getStore('accessToken')) as string;

        if (!user || !group) return goto('/setup');

        const deviceIds = group.devices['server'] || [];
        const results = await Promise.all(deviceIds.map((id: string) => getDeviceApi(id, 'server', accessToken)));
        servers = results.filter((d: any) => d !== null);
        loading = false;
    });

    function openSettings(server: ServerDevice) {
        selectedDevice = { ...server, type: 'server' };
        settingsPopup = true;
    }
</script>

<div class="min-h-screen w-full bg-dark-background-900 text-dark-text p-4 md:p-8">
    <div class="max-w-4xl mx-auto" in:fly={{ y: 20, duration: 400 }}>
        <header class="flex items-center justify-between mb-8">
            <div>
                <button on:click={() => goto('/')} class="text-sm text-dark-accent hover:underline mb-1">&larr; Dashboard</button>
                <h1 class="text-3xl font-bold text-dark-primary tracking-tight">Server Nodes</h1>
            </div>
            <div class="px-3 py-1 rounded-full bg-dark-background-600 border border-dark-accent/20 text-xs font-mono text-dark-accent">
                {group.name}
            </div>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            {#each servers as server}
                <button 
                    class="bg-dark-background-600/50 backdrop-blur-md border border-white/5 rounded-3xl p-6 text-left hover:border-dark-accent/30 transition-all group"
                    on:click={() => openSettings(server)}
                >
                    <div class="flex justify-between items-start mb-4">
                        <h3 class="text-lg font-semibold text-white group-hover:text-dark-primary transition-colors">{server.name}</h3>
                        <div class="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]"></div>
                    </div>
                    <p class="text-xs font-mono text-gray-500 mb-4">{server.id}</p>
                    <div class="flex gap-4">
                        <div class="text-[10px] uppercase font-bold text-gray-500">Messages: {server.messages?.length || 0}</div>
                        <div class="text-[10px] uppercase font-bold text-gray-500">Commands: {server.deviceCommands?.length || 0}</div>
                    </div>
                </button>
            {/each}
        </div>
    </div>

    <DevicePopup runCommand={runCommand} bind:device={selectedDevice} bind:visible={settingsPopup} {accessToken} />
</div>