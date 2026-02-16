<script lang="ts">
    import { invoke } from '@tauri-apps/api/tauri';
    import { page } from '$app/stores';
    import NavButton from '$lib/NavButton.svelte';
    import '../../app.css';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { getStore } from '$lib/tauri';
    import type { Device, PublicUser } from '$lib';
    import type { Group } from '$lib/xata';
    import { currentUrl, navOpen } from '$lib/stores';

    let device: Device = { id: '', name: '' };
    let deviceType: string = 'client';
    let accessToken: string = '';
    let groups: Group[] = [];
    let user: PublicUser | null = null;
    let screenWidth: number = 0;

    onMount(async () => {
        currentUrl.set(window.location.pathname);
        device = (await getStore('device')) as Device;
        user = (await getStore('user')) as PublicUser;
        accessToken = (await getStore('accessToken')) as string;

        if (!user) {
            goto('/setup');
            return;
        }

        if (!device?.id) {
            goto('/device-info');
        }

        const res = await fetch(`https://spark-api.fly.dev/groups/${user.id}`, {
            headers: { authorization: `Bearer ${accessToken}` }
        });
        
        if (res.ok) {
            groups = await res.json();
        }
    });

    let pages: any[] = [];
    $: if (device) {
        pages = [
            { name: device.name || 'This Device', url: '/this-device', icon: 'device' },
            { name: 'Dashboard', url: '/dashboard', icon: 'dashboard' },
            { name: 'Clients', url: '/clients', icon: 'clients' },
            { name: 'Servers', url: '/servers', icon: 'servers' },
            { name: 'Commands', url: '/commands', icon: 'commands' },
            { name: 'Settings', url: '/settings', icon: 'settings' },
            { name: 'Integrations', url: '/integrations', icon: 'integrations' }
        ];
    }

    $: isMobile = screenWidth < 768;
</script>

<svelte:window bind:innerWidth={screenWidth} />

<div class="h-screen w-screen bg-[#0a0b10] text-slate-200 flex flex-col md:flex-row overflow-hidden font-sans">
    <div class="md:hidden flex items-center justify-between p-5 bg-dark-background-800/50 backdrop-blur-xl border-b border-white/5 z-[60]">
        <h1 class="text-dark-accent font-bold tracking-tighter text-xl">S.P.A.R.K</h1>
        <button class="p-2 text-dark-primary" on:click={() => navOpen.set(!$navOpen)}>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7">
                {#if $navOpen}
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                {:else}
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                {/if}
            </svg>
        </button>
    </div>

    <nav class="
        {$navOpen ? 'translate-x-0 w-64' : '-translate-x-full w-0 md:translate-x-0 md:w-20'} 
        lg:w-64 fixed md:relative z-50 h-full bg-dark-background-900/80 backdrop-blur-2xl border-r border-white/5 
        transition-all duration-500 ease-in-out flex flex-col shadow-2xl"
    >
        <div class="p-6 hidden lg:block">
            <h1 class="text-2xl font-black text-white tracking-tighter italic">SPARK<span class="text-dark-accent">.</span></h1>
        </div>

        <div class="flex-1 flex flex-col gap-1 px-3 overflow-y-auto no-scrollbar pt-4 md:pt-0">
            {#each pages as pageItem, i}
                <NavButton
                    name={pageItem.name}
                    url={pageItem.url}
                    type={i === 0 ? deviceType : pageItem.icon}
                    selected={$currentUrl === pageItem.url}
                    compact={!$navOpen && !isMobile && screenWidth < 1024}
                    onclick={() => {
                        currentUrl.set(pageItem.url);
                        if (isMobile) navOpen.set(false);
                        goto(pageItem.url);
                    }}
                />
            {/each}

            {#if groups.length > 0}
                <div class="mt-8 px-4 mb-2">
                    <hr class="border-white/5 mb-4" />
                    <p class="text-[10px] uppercase tracking-[0.2em] text-dark-secondary font-bold">Infrastructures</p>
                </div>
                {#each groups as group}
                    <NavButton
                        name={group.name}
                        url={`/group/${group.id}`}
                        type="group"
                        selected={$currentUrl === `/group/${group.id}`}
                        compact={!$navOpen && !isMobile && screenWidth < 1024}
                    />
                {/each}
            {/if}
        </div>

        <div class="p-4 border-t border-white/5 bg-black/20">
            <div class="flex items-center gap-3 px-2">
                <div class="w-8 h-8 rounded-full bg-dark-accent/20 flex items-center justify-center text-dark-accent font-bold text-xs border border-dark-accent/30">
                    {user?.username?.charAt(0).toUpperCase() || 'U'}
                </div>
                {#if $navOpen || screenWidth >= 1024}
                    <div class="flex flex-col truncate">
                        <span class="text-sm font-medium text-slate-200 truncate">{user?.username}</span>
                        <span class="text-[10px] text-green-500 uppercase font-bold tracking-widest">Online</span>
                    </div>
                {/if}
            </div>
        </div>
    </nav>

    {#if isMobile && $navOpen}
        <div class="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity" on:click={() => navOpen.set(false)}></div>
    {/if}

    <main class="flex-1 overflow-y-auto relative bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-dark-accent/5 via-transparent to-transparent">
        <slot />
    </main>
</div>