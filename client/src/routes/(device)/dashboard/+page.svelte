<script lang="ts">
    import { onMount } from 'svelte';
    import { fly } from 'svelte/transition';
    import { getStore } from '$lib/tauri';
    import { goto } from '$app/navigation';
    import type { Group } from '$lib/xata';

    let group: Group = { name: '', devices: { client: [], server: [] } };
    let user: any = null;
    let loading = true;

    onMount(async () => {
        group = (await getStore('group')) as Group;
        user = (await getStore('user'));
        loading = false;
        
        if (!user) goto('/setup');
    });

    $: clientCount = group.devices?.client?.length || 0;
    $: serverCount = group.devices?.server?.length || 0;
    $: totalDevices = clientCount + serverCount;
</script>

<div class="min-h-screen p-6 lg:p-12">
    <div class="max-w-6xl mx-auto space-y-10" in:fly={{ y: 20, duration: 600 }}>
        
        <header>
            <h1 class="text-4xl font-black text-white tracking-tighter italic uppercase">
                Control <span class="text-dark-accent">Center</span>
            </h1>
            <p class="text-gray-500 mt-2 font-medium tracking-wide">Cluster: <span class="text-slate-300">@{group.name || 'Standalone'}</span></p>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="spark-card p-6 border-l-4 border-l-dark-accent">
                <p class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">Total Fleet</p>
                <h3 class="text-3xl font-light text-white">{totalDevices}</h3>
            </div>
            <div class="spark-card p-6">
                <p class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">Active Clients</p>
                <h3 class="text-3xl font-light text-white">{clientCount}</h3>
            </div>
            <div class="spark-card p-6">
                <p class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">Active Servers</p>
                <h3 class="text-3xl font-light text-white">{serverCount}</h3>
            </div>
            <div class="spark-card p-6 bg-green-500/5">
                <p class="text-[10px] font-bold text-green-500/50 uppercase tracking-widest mb-1">System Load</p>
                <h3 class="text-3xl font-light text-green-500">Nominal</h3>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <section class="space-y-4">
                <h2 class="text-xs font-black uppercase tracking-[0.3em] text-gray-500 px-2">Navigation</h2>
                <div class="grid grid-cols-1 gap-4">
                    <button on:click={() => goto('/clients')} class="spark-card spark-card-hover p-6 flex items-center justify-between group">
                        <div class="flex items-center gap-4">
                            <div class="p-3 rounded-xl bg-blue-500/10 text-blue-400 group-hover:scale-110 transition-transform">
                                <svg xmlns="http://www.w3.org/2000/svg" class="size-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                                </svg>
                            </div>
                            <div class="text-left">
                                <h4 class="font-bold text-white">Client Nodes</h4>
                                <p class="text-xs text-gray-500">Manage mobile and desktop edge devices</p>
                            </div>
                        </div>
                        <svg xmlns="http://www.w3.org/2000/svg" class="size-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                    </button>

                    <button on:click={() => goto('/servers')} class="spark-card spark-card-hover p-6 flex items-center justify-between group">
                        <div class="flex items-center gap-4">
                            <div class="p-3 rounded-xl bg-purple-500/10 text-purple-400 group-hover:scale-110 transition-transform">
                                <svg xmlns="http://www.w3.org/2000/svg" class="size-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2" />
                                </svg>
                            </div>
                            <div class="text-left">
                                <h4 class="font-bold text-white">Server Infrastructure</h4>
                                <p class="text-xs text-gray-500">Monitor high-compute cluster nodes</p>
                            </div>
                        </div>
                        <svg xmlns="http://www.w3.org/2000/svg" class="size-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                    </button>
                </div>
            </section>

            <section class="space-y-4">
                <h2 class="text-xs font-black uppercase tracking-[0.3em] text-gray-500 px-2">Group Intel</h2>
                <div class="spark-card p-8 h-full bg-gradient-to-br from-dark-background-600/50 to-dark-accent/5">
                    <div class="flex flex-col h-full">
                        <h3 class="text-xl font-bold text-white mb-4">Cluster Health</h3>
                        <div class="space-y-6">
                            <div class="flex justify-between items-center text-sm">
                                <span class="text-gray-400">Sync Status</span>
                                <span class="text-dark-accent font-mono">Synchronized</span>
                            </div>
                            <div class="flex justify-between items-center text-sm">
                                <span class="text-gray-400">Primary Protocol</span>
                                <span class="text-white font-mono uppercase">{user?.settings?.primaryCommunicationMethod || 'NATS'}</span>
                            </div>
                            <div class="pt-6 border-t border-white/5">
                                <p class="text-xs text-gray-500 leading-relaxed italic">
                                    Welcome back, {user?.username}. Your cluster is currently operating across {totalDevices} nodes. No critical alerts were detected in the last sync window.
                                </p>
                            </div>
                        </div>
                        <button 
                            class="spark-btn-primary w-full mt-auto py-3"
                            on:click={() => goto('/settings')}
                        >
                            Global Settings
                        </button>
                    </div>
                </div>
            </section>
        </div>
    </div>
</div>