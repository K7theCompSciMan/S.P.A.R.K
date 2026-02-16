<script lang="ts">
    import { onMount } from 'svelte';
    import { invoke } from '@tauri-apps/api/tauri';
    import { goto } from '$app/navigation';
    import { getStore, setStore } from '$lib/tauri';
    import type { Command, Device, PublicUser } from '$lib';
    import CommandCard from '$lib/CommandCard.svelte';
    import CreateCommandPopup from '$lib/CommandPopup.svelte';
    import { updateDeviceApi } from '$lib/api';

    let user: PublicUser | null = null;
    let device: Device = { deviceCommands: [] };
    let accessToken = '';
    let createCommandPopup = false;
    let popup = false;
    let newCommand: Command = { name: '', command: '', aliases: [''] };

    onMount(async () => {
        device = (await getStore('device')) as Device;
        user = (await getStore('user')) as PublicUser;
        accessToken = (await getStore('accessToken')) as string;

        if (!user) goto('/login');
    });

    $: deviceCommands = device.deviceCommands || [];

    async function syncCommands() {
        const res = await updateDeviceApi(device, accessToken, device.id);
        if (res.ok) {
            device = await res.json();
            await setStore('device', device);
        }
    }

    async function deleteCommand(command: Command) {
        device.deviceCommands = device.deviceCommands?.filter((c) => c !== command);
        await syncCommands();
    }

    async function runCommand(command: Command) {
        invoke('run_command', { command: command.command });
    }
</script>

<div class="p-8 h-full flex flex-col items-center">
    <header class="w-full max-w-4xl flex justify-between items-end mb-10">
        <div>
            <h1 class="text-3xl font-bold text-white tracking-tight">System Commands</h1>
            <p class="text-dark-accent font-mono text-sm uppercase tracking-widest mt-1">
                Active on: <span class="text-slate-300">{device.name}</span>
            </p>
        </div>
        
        <button 
            class="px-6 py-3 bg-dark-accent text-white rounded-xl font-bold text-sm hover:scale-105 transition-all shadow-lg shadow-dark-accent/20 flex items-center gap-2"
            on:click={() => {
                createCommandPopup = true;
                setTimeout(() => document.getElementById('createGroupInput')?.focus(), 100);
            }}
        >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            Create New
        </button>
    </header>

    <div class="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 gap-4 overflow-y-auto no-scrollbar pb-20">
        {#each deviceCommands as command}
            <div class="bg-dark-background-500/40 backdrop-blur-md border border-white/5 rounded-2xl p-2 hover:border-dark-accent/30 transition-all">
                <CommandCard bind:popup {command} updateCommands={syncCommands} {deleteCommand} {runCommand} />
            </div>
        {/each}

        {#if deviceCommands.length === 0}
            <div class="col-span-full py-20 border-2 border-dashed border-white/5 rounded-[2rem] flex flex-col items-center justify-center opacity-40">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1" stroke="currentColor" class="size-16 mb-4">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 7.5l3 2.25-3 2.25m4.5 0h3m-9 8.25h13.5A2.25 2.25 0 0021 18V6a2.25 2.25 0 00-2.25-2.25H5.25A2.25 2.25 0 003 6v12a2.25 2.25 0 002.25 2.25z" />
                </svg>
                <p class="text-xl">No commands defined yet</p>
            </div>
        {/if}
    </div>

    <CreateCommandPopup
        location="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
        {device}
        bind:newCommand
        bind:visible={createCommandPopup}
        updateCommand={async () => {
            device.deviceCommands = [...(device.deviceCommands || []), newCommand];
            await syncCommands();
            createCommandPopup = false;
        }}
    />
</div>