<script lang="ts">
    import CreateCommandPopup from './CommandPopup.svelte';
    import type { Command } from '$lib';
    import { createEventDispatcher } from 'svelte';

    export let command: Command;
    export let updateCommands: () => Promise<void> = async () => {};
    export let deleteCommand: (command: Command) => Promise<void> = async () => {};
    export let runCommand: (command: Command) => Promise<void> = async () => {};
    
    // Internal state for the popup
    let popup = false;

    // Helper to format aliases list
    $: aliasString = command.aliases && command.aliases.length > 0 
        ? command.aliases.join(', ') 
        : 'No aliases';
</script>

<div 
    class="group relative w-full bg-dark-background-300 hover:bg-dark-background-400 border border-transparent hover:border-dark-secondary/30 rounded-xl transition-all duration-200 cursor-pointer overflow-hidden shadow-sm hover:shadow-lg mb-3"
    on:click={() => popup = true}
    role="button"
    tabindex="0"
    on:keypress={(e) => e.key === 'Enter' && (popup = true)}
>
    <div class="flex flex-col md:flex-row h-full">
        
        <div class="flex-1 p-5 flex flex-col justify-center border-r border-white/5">
            <h3 class="text-lg font-semibold text-dark-primary mb-1">{command.name}</h3>
            <div class="text-sm text-gray-400 flex items-center gap-2">
                <span class="text-xs uppercase tracking-wider font-bold text-dark-secondary">Aliases:</span>
                <span class="truncate">{aliasString}</span>
            </div>
        </div>

        <div class="w-full md:w-1/2 bg-black/20 p-4 font-mono text-sm text-gray-300 flex items-center relative group-hover:bg-black/30 transition-colors">
            <div class="w-full overflow-hidden text-ellipsis whitespace-nowrap pr-16">
                <span class="text-dark-accent">$</span> {command.command}
            </div>

            <div class="absolute right-3 flex items-center gap-2 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity duration-200">
                <button 
                    on:click|stopPropagation={async () => await runCommand(command)}
                    class="p-2 rounded-lg bg-green-500/10 text-green-500 hover:bg-green-500 hover:text-white transition-all"
                    title="Run Command"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
                    </svg>
                </button>

                <button 
                    on:click|stopPropagation={async () => await deleteCommand(command)}
                    class="p-2 rounded-lg bg-red-500/10 text-red-500 hover:bg-red-500 hover:text-white transition-all"
                    title="Delete Command"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                    </svg>
                </button>
            </div>
        </div>
    </div>
</div>

<CreateCommandPopup 
    bind:visible={popup} 
    type="Edit" 
    newCommand={command} 
	updateCommand={updateCommands} 
    on:close={() => popup = false}
/>