<script lang="ts">
    import { onMount } from 'svelte';
    import { fade, fly } from 'svelte/transition';
    import { goto } from '$app/navigation';
    import { invoke } from '@tauri-apps/api/tauri';
    import { getStore, setStore } from '$lib/tauri';
    import DevicePopup from '$lib/DevicePopup.svelte';
    import type { Command, Device } from '$lib';
    import type { User, Group } from '$lib/xata';

    let loading = true;
    let thisDevice: Device = { name: '', id: '', messages: [], deviceCommands: [] };
    let user: User = {};
    let group: Group = {};
    let accessToken = '';

    onMount(async () => {
        try {
            const [storedDevice, storedType, storedUser, storedGroup, storedToken] = await Promise.all([
                getStore('device'),
                getStore('deviceType'),
                getStore('user'),
                getStore('group'),
                getStore('accessToken')
            ]);

            thisDevice = storedDevice as Device;
            if (thisDevice) thisDevice.type = (storedType as string) || 'client';
            user = storedUser as User;
            group = storedGroup as Group;
            accessToken = storedToken as string;

            if (!thisDevice?.id || !user) goto('/setup');
        } finally {
            loading = false;
        }
    });

    async function runCommand(command: Command) {
        await invoke('run_command', { command: command.command });
    }
</script>

<div class="min-h-screen p-6 lg:p-12">
    {#if loading}
        <div class="max-w-5xl mx-auto animate-pulse space-y-8">
            <div class="h-10 bg-white/5 w-1/4 rounded-lg"></div>
            <div class="h-64 bg-white/5 rounded-[2rem]"></div>
        </div>
    {:else}
        <div class="max-w-5xl mx-auto space-y-8" in:fly={{ y: 20, duration: 500 }}>
            
            <header class="flex justify-between items-end">
                <div>
                    <button on:click={() => goto('/dashboard')} class="text-sm text-dark-accent hover:text-white transition-colors mb-2 block">
                        &larr; Return to Dashboard
                    </button>
                    <h1 class="text-4xl font-black text-white tracking-tighter">Device <span class="text-dark-accent">Focus</span></h1>
                </div>
                <div class="flex flex-col items-end">
                    <span class="text-[10px] font-bold uppercase tracking-[0.2em] text-gray-500 mb-1">Local Identity</span>
                    <div class="px-4 py-1 rounded-full bg-dark-accent/10 border border-dark-accent/30 text-xs font-mono text-dark-accent">
                        {thisDevice.type?.toUpperCase()}
                    </div>
                </div>
            </header>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="spark-card p-6 flex flex-col items-center justify-center text-center">
                    <span class="text-gray-500 text-[10px] font-bold uppercase tracking-widest mb-2">Stored Messages</span>
                    <span class="text-3xl font-light text-white">{thisDevice.messages?.length || 0}</span>
                </div>
                <div class="spark-card p-6 flex flex-col items-center justify-center text-center">
                    <span class="text-gray-500 text-[10px] font-bold uppercase tracking-widest mb-2">Active Commands</span>
                    <span class="text-3xl font-light text-white">{thisDevice.deviceCommands?.length || 0}</span>
                </div>
                <div class="spark-card p-6 flex flex-col items-center justify-center text-center">
                    <span class="text-gray-500 text-[10px] font-bold uppercase tracking-widest mb-2">Uptime Status</span>
                    <span class="text-xs font-bold text-green-500 flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                        OPERATIONAL
                    </span>
                </div>
            </div>

            <div class="spark-card overflow-hidden">
                <div class="p-8 md:p-12">
                    <div class="flex items-center gap-6 mb-10">
                        <div class="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center text-dark-accent border border-white/10 shadow-inner">
                            <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 17L9 21h6l-.75-4M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                            </svg>
                        </div>
                        <div>
                            <h2 class="text-2xl font-bold text-white leading-none mb-2">{thisDevice.name}</h2>
                            <p class="text-sm font-mono text-gray-500">Node Hardware ID: {thisDevice.id}</p>
                        </div>
                    </div>

                    <div class="bg-black/20 rounded-2xl p-2 border border-white/5">
                        <DevicePopup 
                            device={thisDevice} 
                            thisDevice={thisDevice} 
                            visible={true} 
                            {runCommand} 
                            {accessToken}
                        />
                    </div>
                </div>
                
                <footer class="bg-white/5 p-6 border-t border-white/5 flex justify-between items-center">
                    <p class="text-xs text-gray-500 italic">Configuration syncs automatically to the Spark Cloud API</p>
                    <span class="text-[10px] text-dark-accent font-bold uppercase tracking-widest">{user?.email}</span>
                </footer>
            </div>
        </div>
    {/if}
</div>