<script lang="ts">
  import { onMount } from 'svelte';
  import { fly } from 'svelte/transition';
  import { getStore } from '$lib/tauri';
  import { goto } from '$app/navigation';
  import type { Group } from '$lib/xata';
  import { isGroupReady, isPublicUserReady } from '$lib/storeAccess';

  let group = {
    id: '',
    name: '',
    devices: { client: [] as string[], server: [] as string[] }
  } as Group;
  let user: any = null;
  let loading = true;

  onMount(async () => {
    const g = await getStore('group');
    if (isGroupReady(g)) {
      group = g;
    }

    const u = await getStore('user');
    if (!isPublicUserReady(u)) {
      await goto('/setup');
      loading = false;
      return;
    }

    user = u;
    loading = false;
  });

  $: clientCount = group.devices?.client?.length || 0;
  $: serverCount = group.devices?.server?.length || 0;
  $: totalDevices = clientCount + serverCount;
</script>

<div class="min-h-screen p-6 lg:p-10 text-zinc-100">
  {#if loading}
    <div class="max-w-5xl mx-auto space-y-8 animate-pulse" aria-busy="true">
      <div class="h-8 bg-white/5 rounded-lg w-1/4"></div>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {#each [1, 2, 3, 4] as _}
          <div class="h-28 bg-white/[0.03] border border-white/[0.04] rounded-2xl"></div>
        {/each}
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="h-64 bg-white/[0.03] border border-white/[0.04] rounded-2xl"></div>
        <div class="h-64 bg-white/[0.03] border border-white/[0.04] rounded-2xl"></div>
      </div>
    </div>
  {:else}
    <div class="max-w-5xl mx-auto space-y-8" in:fly={{ y: 12, duration: 400 }}>
      <header class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 class="text-3xl font-bold tracking-tight text-white">
            Control <span class="text-transparent bg-clip-text bg-gradient-to-r from-dark-primary to-dark-accent">Center</span>
          </h1>
          <p class="text-sm text-zinc-400 mt-1 flex items-center gap-2 font-medium">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            Cluster: <span class="text-zinc-200 bg-white/[0.06] border border-white/[0.05] px-2 py-0.5 rounded text-xs font-mono">@{group.name || 'standalone'}</span>
          </p>
        </div>
      </header>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="spark-card p-5 border-l-2 border-l-dark-primary bg-dark-background-900/20">
          <p class="text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-1">Total Fleet</p>
          <h3 class="text-3xl font-semibold text-white tracking-tight">{totalDevices}</h3>
        </div>
        <div class="spark-card p-5">
          <p class="text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-1">Active Clients</p>
          <h3 class="text-3xl font-semibold text-white tracking-tight">{clientCount}</h3>
        </div>
        <div class="spark-card p-5">
          <p class="text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-1">Active Servers</p>
          <h3 class="text-3xl font-semibold text-white tracking-tight">{serverCount}</h3>
        </div>
        <div class="spark-card p-5 bg-emerald-500/[0.02]">
          <p class="text-[10px] font-bold text-emerald-500 uppercase tracking-wider mb-1">System Load</p>
          <h3 class="text-2xl font-medium text-emerald-400 tracking-tight">Nominal</h3>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div class="lg:col-span-7 space-y-3.5">
          <h2 class="text-[10px] font-bold uppercase tracking-[0.25em] text-zinc-500 px-1">Infrastructure Management</h2>
          
          <button on:click={() => goto('/clients')} class="w-full spark-card spark-card-hover p-5 flex items-center justify-between group text-left">
            <div class="flex items-center gap-4">
              <div class="p-3 rounded-xl bg-dark-primary/10 text-dark-primary group-hover:scale-105 transition-transform">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h4 class="text-sm font-semibold text-white">Client Edge Nodes</h4>
                <p class="text-xs text-zinc-400 mt-0.5">Manage mobile platforms and desktop execution units</p>
              </div>
            </div>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-zinc-600 group-hover:text-zinc-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" /></svg>
          </button>

          <button on:click={() => goto('/servers')} class="w-full spark-card spark-card-hover p-5 flex items-center justify-between group text-left">
            <div class="flex items-center gap-4">
              <div class="p-3 rounded-xl bg-dark-accent/10 text-dark-accent group-hover:scale-105 transition-transform">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2" />
                </svg>
              </div>
              <div>
                <h4 class="text-sm font-semibold text-white">Server Environments</h4>
                <p class="text-xs text-zinc-400 mt-0.5">Monitor persistent cluster runtimes and orchestrators</p>
              </div>
            </div>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-zinc-600 group-hover:text-zinc-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" /></svg>
          </button>
        </div>

        <div class="lg:col-span-5 space-y-3.5 flex flex-col">
          <h2 class="text-[10px] font-bold uppercase tracking-[0.25em] text-zinc-500 px-1">Cluster Parameters</h2>
          <div class="spark-card p-6 flex-1 flex flex-col justify-between">
            <div>
              <h3 class="text-sm font-semibold text-white mb-4">Diagnostics Sync</h3>
              <div class="space-y-3.5 text-xs">
                <div class="flex justify-between items-center">
                  <span class="text-zinc-400">Database Fabric</span>
                  <span class="text-dark-primary font-medium bg-dark-primary/10 px-2 py-0.5 rounded text-[11px]">Xata Connected</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-zinc-400">Primary Protocol</span>
                  <span class="text-zinc-200 font-mono text-[11px] uppercase bg-white/[0.05] px-1.5 py-0.5 rounded">{user?.settings?.primaryCommunicationMethod || 'NATS / TLS'}</span>
                </div>
                <div class="pt-4 border-t border-white/[0.04]">
                  <p class="text-zinc-400 leading-relaxed text-[11px] italic">
                    Operator identifier: <span class="text-zinc-200 not-italic font-mono">@{user?.username}</span>. Cluster operating at optimal efficiency across {totalDevices} micro-nodes. No anomalies reported.
                  </p>
                </div>
              </div>
            </div>
            <button class="spark-btn-primary w-full mt-6 py-2.5 text-xs tracking-wide" on:click={() => goto('/settings')}>
              Global Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>