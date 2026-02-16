<script lang="ts">
    import { onMount } from 'svelte';
    import { fly } from 'svelte/transition';
    import { getStore, setStore } from '$lib/tauri';
    import type { Command, Device } from '$lib';
    import CommandCard from '$lib/CommandCard.svelte';
    import CreateCommandPopup from '$lib/CommandPopup.svelte';
    import { updateDeviceApi } from '$lib/api';

    let device: Device = { deviceCommands: [] };
    let accessToken = '';
    let createCommandPopup = false;
    let newCommand: Command = { name: '', command: '', aliases: [''] };

    onMount(async () => {
        device = (await getStore('device')) as Device;
        accessToken = (await getStore('accessToken')) as string;
    });

    async function syncCommands() {
        const res = await updateDeviceApi(device, accessToken, device.id);
        if (res.ok) await setStore('device', device);
    }
</script>

<div class="min-h-screen w-full bg-dark-background-900 p-4 md:p-8 overflow-y-auto">
    <div class="max-w-4xl mx-auto" in:fly={{ y: 20, duration: 400 }}>
        <header class="flex items-end justify-between mb-8">
            <div>
                <h1 class="text-3xl font-bold text-dark-primary tracking-tight">System Commands</h1>
                <p class="text-sm text-gray-500 mt-1">Executing on <span class="text-dark-accent font-mono">{device.name}</span></p>
            </div>
            <button 
                class="px-5 py-2.5 bg-dark-primary text-white rounded-xl font-bold text-sm hover:scale-105 transition-all shadow-lg shadow-dark-primary/20"
                on:click={() => createCommandPopup = true}
            >
                + New Command
            </button>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            {#each device.deviceCommands || [] as command}
                <div class="bg-dark-background-600/50 backdrop-blur-md border border-white/5 rounded-3xl p-2">
                    <CommandCard {command} updateCommands={syncCommands} />
                </div>
            {/each}
        </div>
    </div>

    <CreateCommandPopup
        bind:visible={createCommandPopup}
        {device}
        bind:newCommand
        updateCommand={async () => {
            device.deviceCommands = [...(device.deviceCommands || []), newCommand];
            await syncCommands();
            createCommandPopup = false;
        }}
    />
</div>