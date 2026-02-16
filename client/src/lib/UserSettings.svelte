<script lang="ts">
    import type { PublicUser } from '$lib';
    import AnimatedInputLabel from './AnimatedInputLabel.svelte';
    import { fly } from 'svelte/transition';

    export let user: PublicUser;

    const methods = [
        { value: 'nats', title: 'NATS', desc: 'Pub/Sub messaging. Low latency, recommended.' },
        { value: 'localhost', title: 'Local', desc: 'Requires same WiFi or Tailscale VPN.' },
        { value: 'api', title: 'Cloud API', desc: 'Standard messaging through central server.' }
    ];
</script>

<div class="max-w-4xl mx-auto" in:fly={{ y: 20, duration: 400 }}>
    <div class="bg-dark-background-600/50 backdrop-blur-md border border-white/5 rounded-3xl shadow-xl overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-dark-primary to-dark-accent opacity-50"></div>
        
        <div class="p-8 md:p-10">
            <h2 class="text-2xl font-bold text-white mb-8">User Preferences</h2>
            
            <div class="space-y-10">
                <section>
                    <label class="text-xs font-bold uppercase tracking-widest text-dark-accent mb-4 block">Identity</label>
                    <AnimatedInputLabel
                        name="Username"
                        labelbg="bg-[#1a1c23]" 
                        bind:value={user.username}
                        size="scale-100"
                    />
                </section>

                <section>
                    <label class="text-xs font-bold uppercase tracking-widest text-dark-accent mb-4 block">Communication Protocol</label>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {#each methods as method}
                            <button 
                                class="p-5 rounded-2xl border transition-all duration-200 text-left flex flex-col gap-2
                                {user.settings.primaryCommunicationMethod === method.value 
                                    ? 'bg-dark-primary/10 border-dark-primary shadow-[0_0_15px_rgba(0,180,216,0.1)]' 
                                    : 'bg-dark-background-800/50 border-white/5 hover:border-white/20'}"
                                on:click={() => user.settings.primaryCommunicationMethod = method.value}
                            >
                                <span class="font-bold {user.settings.primaryCommunicationMethod === method.value ? 'text-dark-primary' : 'text-slate-300'}">
                                    {method.title}
                                </span>
                                <span class="text-xs text-gray-500 leading-snug">{method.desc}</span>
                            </button>
                        {/each}
                    </div>
                </section>
            </div>
        </div>

        <div class="bg-dark-background-800/50 p-6 border-t border-white/5 flex items-start gap-4">
             <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-dark-accent shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
             <p class="text-xs text-gray-400">These settings are global and will affect how this user interacts with all clusters.</p>
        </div>
    </div>
</div>