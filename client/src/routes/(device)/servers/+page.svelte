<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { invoke } from '@tauri-apps/api/tauri';
    import DevicePopup from '$lib/DevicePopup.svelte';
    import { getStore } from '$lib/tauri';
    import { getDeviceApi, updateDeviceApi } from '$lib/api';
    import type { Device, Command } from '$lib';
    import type { ServerDevice, User, Group } from '$lib/xata';

    let thisDevice: Device = {};
    let user: User = {};
    let group: Group = { name: '', devices: { client: [], server: [] } };
    let servers: ServerDevice[] = [];
    let accessToken = '';
    
    let settingsPopup = false;
    let selectedDevice: Device = { id: '', name: '', messages: [], deviceCommands: [], type: 'server' };
    let newCommand: Command = { name: '', command: '', aliases: [''] };

    onMount(async () => {
        thisDevice = (await getStore('device')) as Device;
        user = (await getStore('user')) as User;
        group = (await getStore('group')) as Group;
        accessToken = (await getStore('accessToken')) as string;

        if (!thisDevice || !user || !group || !accessToken) {
            goto('/setup');
            return;
        }

        const deviceIds = group.devices['server'] || [];
        const results = await Promise.all(
            deviceIds.map(id => getDeviceApi(id, 'server', accessToken))
        );
        servers = results.filter(d => d !== null);
    });

    async function handleUpdate(device: Device) {
        const res = await updateDeviceApi(device, accessToken, thisDevice.id);
        if (res.ok) {
            servers = servers.map(c => c.id === device.id ? { ...c, ...device } : c);
        }
    }

    function openSettings(server: ServerDevice) {
        selectedDevice = { ...server, type: 'server' };
        settingsPopup = true;
    }

    async function runCommand(command: Command) {
        invoke('run_command', { command: command.command });
    }
</script>

<div class="bg-dark-background-600 w-[85vw] ml-[2.5%] rounded-[2.5rem] shadow-2xl h-[95vh] mt-[2.5vh] overflow-hidden relative border border-white/5">
    <div class="flex flex-col items-center h-full pt-8 px-8">
        <header class="text-center mb-8">
            <h1 class="text-3xl font-light text-slate-100">
                Server Devices <span class="text-dark-accent font-medium">@{group.name}</span>
            </h1>
            <p class="text-dark-secondary text-sm mt-2">Manage and configure your edge nodes</p>
        </header>

        {#if servers.length === 0}
            <div class="flex flex-col items-center justify-center h-64 opacity-50">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-dark-accent mb-4"></div>
                <p class="text-dark-text">Scanning for devices...</p>
            </div>
        {:else}
            <div class="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 gap-4 overflow-y-auto no-scrollbar pb-12">
                <!-- svelte-ignore a11y_no_static_element_interactions -->
                {#each servers as server}
                    <!-- svelte-ignore a11y_click_events_have_key_events -->
                    <div 
                        class="bg-dark-background-500/50 backdrop-blur-md border border-white/10 rounded-2xl p-5 flex flex-col relative 
                            		hover:border-dark-accent/50 hover:translate-y-[-2px] transition-all duration-300 group cursor-pointer"
                        on:click|self={() => openSettings(server)}
                    >
                        <div class="flex justify-between items-start mb-4">
                            <input
                                type="text"
                                class="bg-transparent text-xl font-semibold text-dark-text border-b border-transparent focus:border-dark-accent focus:outline-none w-2/3 transition-colors"
                                bind:value={server.name}
                                on:focusout={() => handleUpdate(server)}
                                on:keydown={(e) => e.key === 'Enter' && handleUpdate(server)}
                            />
                            <button 
                                class="p-2 rounded-lg bg-dark-background-400 text-dark-secondary group-hover:text-dark-accent transition-colors"
                                on:click={() => openSettings(server)}
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" class="size-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                            </button>
                        </div>

                        <div class="flex gap-4 mt-auto">
                            <div class="flex items-center gap-1.5 text-xs text-dark-secondary">
                                <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                                Messages: {server.messages?.length || 0}
                            </div>
                            <div class="flex items-center gap-1.5 text-xs text-dark-secondary">
                                <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                                Commands: {server.deviceCommands?.length || 0}
                            </div>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
    </div>

    <DevicePopup
        bind:device={selectedDevice}
        bind:visible={settingsPopup}
        {runCommand}
        {accessToken}
        {thisDevice}
    />
</div>