<script lang="ts">
    import { invoke } from '@tauri-apps/api/tauri';
    import { fade, fly } from 'svelte/transition';
    import type { Device, Command } from '$lib';
    import { onMount, createEventDispatcher } from 'svelte';
    import type { Group } from './xata';
    import { getStore } from './tauri';
    import { DEFAULT_PRESETS } from '$lib/presets'; // Import from the helper file

    const dispatch = createEventDispatcher();

    export let device: Device = {};
    export let newCommand: Command = { name: '', command: '', aliases: [''] };
    export let updateCommand: () => Promise<void> = async () => {};
    export let visible: boolean = false;
    export let type: 'Create' | 'Edit' = 'Create';

    let group: Group = {};
    let showPresets = false;
    
    // Combine group presets and defaults
    $: allPresets = [
        ...(group?.commandPresets || []),
        ...DEFAULT_PRESETS
    ];

    onMount(async () => {
        group = (await getStore('group')) as Group;
    });

    async function runCurrent() {
        await invoke('run_command', { command: newCommand.command });
    }

    function applyPreset(preset: Command) {
        newCommand = { ...preset, aliases: [...preset.aliases] }; // Clone it
        showPresets = false;
    }

    function close() {
        visible = false;
        dispatch('close');
    }
</script>

{#if visible}
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div 
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
        transition:fade={{ duration: 200 }}
        on:click|self={close}
    >
        <div 
            class="bg-dark-background-800 w-full max-w-4xl h-[85vh] rounded-2xl shadow-2xl border border-white/10 flex flex-col relative overflow-hidden"
            transition:fly={{ y: 20, duration: 300 }}
        >
            
            <div class="h-16 border-b border-white/5 flex items-center justify-between px-6 bg-dark-background-900/50">
                <h2 class="text-xl font-bold text-white">
                    <span class="text-dark-primary">{type}</span> Command
                </h2>
                
                <div class="flex items-center gap-2">
                    <button 
                        class="px-3 py-1.5 text-sm rounded-lg bg-dark-background-600 hover:bg-dark-primary hover:text-white transition-colors flex items-center gap-2 text-gray-300"
                        on:click={() => showPresets = !showPresets}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-4">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" />
                        </svg>
                        {showPresets ? 'Hide Presets' : 'Load Preset'}
                    </button>

                    <button on:click={close} class="p-2 hover:text-red-500 transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
            </div>

            <div class="flex-1 flex overflow-hidden relative">
                
                {#if showPresets}
                    <div 
                        class="absolute inset-y-0 left-0 z-20 w-80 bg-dark-background-700 border-r border-white/10 overflow-y-auto p-4"
                        transition:fly={{ x: -20, duration: 200 }}
                    >
                        <h3 class="text-sm font-bold text-gray-400 uppercase mb-4 tracking-wider">Available Presets</h3>
                        <div class="space-y-2">
                            {#each allPresets as preset}
                                <button 
                                    class="w-full text-left p-3 rounded-lg bg-dark-background-600 hover:bg-dark-primary/20 hover:border-dark-primary border border-transparent transition-all group"
                                    on:click={() => applyPreset(preset)}
                                >
                                    <div class="font-medium text-white group-hover:text-dark-primary">{preset.name}</div>
                                    <div class="text-xs text-gray-400 font-mono truncate mt-1 opacity-70">{preset.command}</div>
                                </button>
                            {/each}
                        </div>
                    </div>
                {/if}

                <div class="flex-1 grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-white/10 overflow-hidden">
                    
                    <div class="p-8 overflow-y-auto">
                        <div class="space-y-6">
                            <div class="flex flex-col gap-2">
                                <label for="cmd-name" class="text-sm font-semibold text-gray-400">Command Name</label>
                                <input 
                                    id="cmd-name"
                                    type="text" 
                                    bind:value={newCommand.name}
                                    placeholder="e.g. Open Browser"
                                    class="bg-dark-background-900 border border-white/10 rounded-lg p-3 text-white focus:border-dark-primary focus:outline-none transition-colors"
                                />
                            </div>

                            <div class="flex flex-col gap-2">
                                <label for="cmd-alias" class="text-sm font-semibold text-gray-400">Aliases (Triggers)</label>
                                <div class="bg-dark-background-900 border border-white/10 rounded-lg p-3 min-h-[100px] flex flex-wrap gap-2 content-start">
                                    {#each newCommand.aliases as alias, i}
                                        <div class="flex items-center gap-1 bg-dark-background-600 text-sm px-2 py-1 rounded-md border border-white/5">
                                            <input 
                                                class="bg-transparent w-auto min-w-[20px] max-w-[120px] focus:outline-none text-white"
                                                bind:value={alias}
                                                placeholder="..."
                                            />
                                            <button 
                                                tabindex="-1"
                                                class="text-gray-400 hover:text-red-400"
                                                on:click={() => newCommand.aliases = newCommand.aliases.filter((_, idx) => idx !== i)}
                                            >
                                                &times;
                                            </button>
                                        </div>
                                    {/each}
                                    <button 
                                        class="px-2 py-1 text-xs bg-dark-primary/20 text-dark-primary rounded hover:bg-dark-primary hover:text-white transition-colors"
                                        on:click={() => newCommand.aliases = [...newCommand.aliases, '']}
                                    >
                                        + Add
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="p-8 bg-black/20 flex flex-col">
                        <div class="flex items-center justify-between mb-2">
                            <label for="cmd-code" class="text-sm font-semibold text-gray-400">Execution Code</label>
                            <button 
                                on:click={runCurrent}
                                class="text-xs flex items-center gap-1 text-green-400 hover:text-green-300"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-3">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
                                </svg>
                                Test Run
                            </button>
                        </div>
                        
                        <div class="flex-1 relative">
                            <textarea 
                                id="cmd-code"
                                bind:value={newCommand.command}
                                class="w-full h-full bg-dark-background-900 font-mono text-sm p-4 rounded-lg border border-white/10 focus:border-dark-primary focus:outline-none resize-none"
                                spellcheck="false"
                            ></textarea>
                        </div>
                    </div>
                </div>
            </div>

            <div class="h-20 border-t border-white/5 flex items-center justify-end px-8 gap-4 bg-dark-background-900/50">
                <button 
                    on:click={close}
                    class="px-6 py-2 rounded-lg text-gray-400 hover:text-white transition-colors"
                >
                    Cancel
                </button>
                <button 
                    on:click={async () => {
                        await updateCommand();
                        close();
                    }}
                    class="px-8 py-2 rounded-lg bg-dark-primary hover:bg-dark-accent text-white font-medium shadow-lg shadow-dark-primary/20 transition-all transform active:scale-95"
                >
                    Save Command
                </button>
            </div>
        </div>
    </div>
{/if}