<script lang="ts">
    import { type Command, type Device } from '$lib';
    import CommandCard from './CommandCard.svelte';
    import CommandPopup from './CommandPopup.svelte';
    import Radio from './Radio.svelte';
    import { updateDeviceApi, deleteMessageApi, getDeviceApi } from '$lib/api';

    export let device: Device = {};
    export let thisDevice: Device = {};
    export let visible: boolean = false;
    export let accessToken: string = '';
    export let runCommand: (command: Command) => Promise<void>;

    let createCommandPopup = false;
    let newCommand: Command = { name: '', command: '', aliases: [''] };

    async function handleUpdate() {
        await updateDeviceApi(device, accessToken, thisDevice.id);
    }

    async function deleteCommand(command: Command) {
        device.deviceCommands = device.deviceCommands?.filter(c => c !== command);
        await handleUpdate();
    }
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
{#if visible}
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" on:click|self={() => visible = false}>
        <div class="bg-dark-background-500 rounded-2xl w-[85%] h-[85%] shadow-2xl relative flex flex-col p-6 overflow-hidden">
            
            <button class="absolute top-4 right-4 text-dark-text hover:text-red-500 transition-colors" on:click={() => { handleUpdate(); visible = false; }}>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-8">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
                </svg>
            </button>

            <h1 class="text-2xl text-dark-primary text-center mb-6">
                Settings for <span class="font-bold text-dark-accent">{device.name}</span>
            </h1>

            <div class="flex flex-row gap-6 h-full overflow-hidden">
                <div class="w-1/2 flex flex-col gap-4">
                    <div class="space-y-4 bg-dark-background-400 p-4 rounded-xl">
                        <div>
                            <label for="name" class="block text-sm text-dark-secondary mb-1">Device Name</label>
                            <input type="text" bind:value={device.name} class="w-full bg-transparent border-b border-dark-secondary text-xl focus:outline-none focus:border-dark-accent text-dark-text" />
                        </div>
                        
                        <div class="h-32 overflow-y-auto no-scrollbar border border-dark-secondary rounded-lg p-2">
                            <label class="text-sm text-dark-secondary">Aliases</label>
                            {#each device.aliases || [] as alias, i}
                                <div class="flex items-center gap-2 mt-1">
                                    <input type="text" bind:value={device.aliases[i]} class="flex-1 bg-transparent border-b border-dark-secondary text-dark-text" />
                                    <button on:click={() => device.aliases = device.aliases.filter((_, idx) => idx !== i)} class="text-red-400 hover:text-red-600">×</button>
                                </div>
                            {/each}
                            <button class="mt-2 text-dark-accent text-sm" on:click={() => device.aliases = [...(device.aliases || []), '']}>+ Add Alias</button>
                        </div>

                        <Radio legend="Device Type" options={[{value:'client', label:'Client'}, {value:'server', label:'Server'}]} bind:userSelected={device.type} />
                    </div>

                    <div class="flex-1 border border-dark-secondary rounded-xl p-4 overflow-hidden flex flex-col">
                        <h2 class="text-xl text-dark-text mb-2 text-center">Recent Messages</h2>
                        <div class="overflow-y-auto space-y-2 no-scrollbar">
                            {#each device.messages || [] as message}
                                {#await getDeviceApi(message.from, 'client', accessToken)}
                                    <div class="animate-pulse bg-dark-background-300 h-12 rounded-lg" />
                                {:then sender}
                                    <div class="bg-dark-background-300 p-3 rounded-lg relative group">
                                        <span class="text-dark-accent text-sm">{sender?.name || 'Unknown'}</span>
                                        <p class="text-green-500">{message.content}</p>
                                        <button class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 text-red-500" on:click={() => deleteMessageApi(message.id, accessToken)}>
                                            <svg xmlns="http://www.w3.org/2000/svg" class="size-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79" /></svg>
                                        </button>
                                    </div>
                                {/await}
                            {/each}
                        </div>
                    </div>
                </div>

                <div class="w-1/2 border border-dark-secondary rounded-xl p-4 flex flex-col overflow-hidden">
                    <h2 class="text-xl text-dark-text mb-4 text-center">Device Commands</h2>
                    <div class="flex-1 overflow-y-auto space-y-3 no-scrollbar">
                        {#each device.deviceCommands || [] as command}
                            <CommandCard {command} updateCommands={handleUpdate} {deleteCommand} {runCommand} />
                        {/each}
                    </div>
                    <button class="mt-4 p-3 bg-dark-background-400 rounded-xl hover:bg-dark-background-300 flex justify-center text-dark-accent transition-colors" on:click={() => createCommandPopup = true}>
                        <svg xmlns="http://www.w3.org/2000/svg" class="size-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" /></svg>
                    </button>
                </div>
            </div>
        </div>
    </div>
{/if}

<CommandPopup
    {device}
    bind:newCommand
    bind:visible={createCommandPopup}
    updateCommand={async () => {
        device.deviceCommands = [...(device.deviceCommands || []), newCommand];
        await handleUpdate();
        createCommandPopup = false;
    }}
/>