<script lang="ts">
    import type { PublicUser } from '$lib';
    import AnimatedInputLabel from './AnimatedInputLabel.svelte';

    export let user: PublicUser;

    const methods = [
        { id: 'nats', label: 'NATS', icon: 'M13.5 16.875h3.375m-9.75 0h3.375m-6.75 0h3.375', desc: 'Real-time Pub/Sub. Best for low latency.' },
        { id: 'localhost', label: 'Local', icon: 'M9 3v18m6-18v18', desc: 'Direct socket. Requires same network/VPN.' },
        { id: 'api', label: 'Cloud API', icon: 'M12 16.5V9.75', desc: 'Standard cloud sync. Easiest setup.' }
    ];
</script>

<div class="bg-dark-background-500/40 backdrop-blur-md border border-white/10 rounded-[2rem] p-8 shadow-2xl w-full max-w-2xl">
    <div class="flex items-center gap-4 mb-8">
        <div class="p-3 bg-dark-accent/20 rounded-2xl border border-dark-accent/30">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6 text-dark-accent">
                <path stroke-linecap="round" stroke-linejoin="round" d="M17.982 18.725A7.488 7.488 0 0 0 12 15.75a7.488 7.488 0 0 0-5.982 2.975m11.963 0a9 9 0 1 0-11.963 0m11.963 0A8.966 8.966 0 0 1 12 21a8.966 8.966 0 0 1-5.982-2.275M15 9.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
            </svg>
        </div>
        <h1 class="text-2xl font-bold text-white">Profile Identity</h1>
    </div>

    <div class="space-y-8">
        <div class="relative group">
            <AnimatedInputLabel
                name="Public Username"
                labelbg="bg-[#1a1c23]" 
                bind:value={user.username}
                size="scale-100"
            />
            <p class="text-xs text-dark-secondary mt-2 px-1">This is how other devices identify you in logs.</p>
        </div>

        <div>
            <label class="text-xs font-bold uppercase tracking-widest text-dark-accent mb-4 block">Communication Protocol</label>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                {#each methods as method}
                    <button 
                        class="p-4 rounded-2xl border transition-all duration-300 text-left flex flex-col gap-2
                        {user.settings.primaryCommunicationMethod === method.id 
                            ? 'bg-dark-accent/10 border-dark-accent shadow-[0_0_15px_rgba(0,180,216,0.2)]' 
                            : 'bg-white/5 border-white/5 hover:border-white/20'}"
                        on:click={() => user.settings.primaryCommunicationMethod = method.id}
                    >
                        <span class="font-bold text-sm {user.settings.primaryCommunicationMethod === method.id ? 'text-dark-accent' : 'text-slate-300'}">
                            {method.label}
                        </span>
                        <span class="text-[10px] text-dark-secondary leading-tight">{method.desc}</span>
                    </button>
                {/each}
            </div>
        </div>

        <div class="bg-blue-500/5 border border-blue-500/20 rounded-xl p-4 flex gap-4">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6 text-blue-400 shrink-0">
                <path stroke-linecap="round" stroke-linejoin="round" d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
            </svg>
            <p class="text-xs text-slate-400 leading-relaxed">
                <strong class="text-slate-200">Protocol Tip:</strong> NATS is the optimized default for SPARK. It ensures your commands arrive in milliseconds without overloading the central API.
            </p>
        </div>
    </div>
</div>