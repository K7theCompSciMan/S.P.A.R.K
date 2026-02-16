<script lang="ts">
    import { onMount } from 'svelte';
    import { fade, fly } from 'svelte/transition';
    import { goto } from '$app/navigation';
    import { invoke } from '@tauri-apps/api/tauri';
    import { getStore, setStore } from '$lib/tauri';
    
    // Components
    import DevicePopup from '$lib/DevicePopup.svelte';
    
    // Types
    import type { Command, Device } from '$lib';
    import type { ClientDevice, User, Group, ServerDevice } from '$lib/xata';

    // State
    let loading = true;
    let thisDevice: Device = {};
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
            if (thisDevice) thisDevice.type = storedType as string;
            user = storedUser as User;
            group = storedGroup as Group;
            accessToken = storedToken as string;

            if (!thisDevice || !user || !group || !accessToken) {
                console.error('Missing required session data, redirecting...');
                goto('/setup');
            }
        } catch (e) {
            console.error('Failed to load store', e);
        } finally {
            loading = false;
        }
    });

    async function updateDevice(deviceToUpdate: Device) {
        if (!deviceToUpdate.id) return;

        const endpoint = deviceToUpdate.type === 'client' ? 'client' : 'server';
        const url = `https://spark-api.fly.dev/device/${endpoint}/`;
        
        try {
            let res = await fetch(url, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    authorization: `Bearer ${accessToken}`
                },
                body: JSON.stringify({ ...deviceToUpdate, id: deviceToUpdate.id })
            });

            if (res.ok) {
                // Determine if we are updating the *current* device context
                if (thisDevice.id === deviceToUpdate.id) {
                    await setStore('device', deviceToUpdate);
                    await setStore('deviceType', deviceToUpdate.type);
                    thisDevice = deviceToUpdate; // Reactivity update
                }
                // Placeholder for a Toast notification
                // toast.success("Device updated successfully");
            } else {
                console.error(await res.text());
                alert('Failed to update device');
            }
        } catch (err) {
            console.error('Network error', err);
        }
    }

    async function deleteMessage(id: string) {
        try {
            let res = await fetch(`https://spark-api.fly.dev/device/message/${id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    authorization: `Bearer ${accessToken}`
                }
            });
            if (!res.ok) console.error(await res.text());
        } catch (e) {
            console.error(e);
        }
    }

    async function deleteCommand(command: Command) {
        if (!thisDevice.deviceCommands) return;
        
        thisDevice.deviceCommands = thisDevice.deviceCommands.filter(
            (c: Command) => c !== command
        );
        await updateDevice(thisDevice);
    }

    async function runCommand(command: Command) {
        await invoke('run_command', { command: command.command });
    }
</script>

<div class="min-h-screen w-full bg-dark-background-900 text-dark-text p-4 md:p-8 overflow-y-auto">
    
    {#if loading}
        <div class="max-w-4xl mx-auto space-y-4 animate-pulse" in:fade>
            <div class="h-8 bg-dark-background-600 rounded w-1/3"></div>
            <div class="h-64 bg-dark-background-600 rounded-2xl w-full"></div>
        </div>
    {:else}
        <div class="max-w-4xl mx-auto" in:fly={{ y: 20, duration: 400 }}>
            
            <header class="flex items-center justify-between mb-6">
                <div>
                    <button on:click={() => goto('/')} class="text-sm text-dark-accent hover:underline mb-1">
                        &larr; Back to Dashboard
                    </button>
                    <h1 class="text-3xl font-bold text-dark-primary tracking-tight">
                        Device Management
                    </h1>
                </div>
                <div class="px-3 py-1 rounded-full bg-dark-background-600 border border-dark-accent/20 text-xs font-mono text-dark-accent">
                    {thisDevice.type?.toUpperCase() || 'UNKNOWN'}
                </div>
            </header>

            <div class="relative bg-dark-background-600/50 backdrop-blur-md border border-white/5 rounded-3xl shadow-xl overflow-hidden">
                
                <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-dark-primary to-dark-accent opacity-50"></div>

                <div class="p-6 md:p-10">
                    <div class="flex items-center gap-4 mb-8">
                        <div class="w-12 h-12 rounded-xl bg-dark-primary/20 flex items-center justify-center text-dark-primary">
                            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M12 5l7 7-7 7" /></svg>
                        </div>
                        <div>
                            <h2 class="text-xl font-semibold text-white">{thisDevice.name}</h2>
                            <p class="text-sm text-gray-400">ID: <span class="font-mono text-xs">{thisDevice.id}</span></p>
                        </div>
                    </div>

                    <div class="bg-dark-background-800/50 rounded-xl p-4 border border-white/5">
                        <DevicePopup 
                            device={thisDevice} 
                            thisDevice={thisDevice} 
                            visible={true} 
                            {runCommand} 
                            {accessToken}
                        />
                    </div>
                </div>
            </div>

            <div class="mt-6 text-center text-xs text-gray-500">
                Authorized as {user?.email || 'Guest'} • Group: {group?.name || 'None'}
            </div>
        </div>
    {/if}
</div>