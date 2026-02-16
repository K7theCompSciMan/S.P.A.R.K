<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { getStore } from '$lib/tauri';
    import { currentUrl, navOpen } from '$lib/stores';
    import NavButton from '$lib/NavButton.svelte';
    import '../../app.css';

    let device: any = null;
    let user: any = null;
    let groups: any[] = [];
    let screenWidth: number = 0;

    onMount(async () => {
        currentUrl.set(window.location.pathname);
        [device, user] = await Promise.all([getStore('device'), getStore('user')]);
        
        if (!user) return goto('/setup');

        const token = await getStore('accessToken');
        const res = await fetch(`https://spark-api.fly.dev/groups/${user.id}`, {
            headers: { authorization: `Bearer ${token}` }
        });
        if (res.ok) groups = await res.json();
    });

    $: isMobile = screenWidth < 768;
    $: pages = device ? [
        { name: device.name || 'This Device', url: '/this-device', icon: 'device' },
        { name: 'Dashboard', url: '/dashboard', icon: 'dashboard' },
        { name: 'Clients', url: '/clients', icon: 'clients' },
        { name: 'Servers', url: '/servers', icon: 'servers' },
        { name: 'Commands', url: '/commands', icon: 'commands' },
        { name: 'Settings', url: '/settings', icon: 'settings' }
    ] : [];
</script>

<svelte:window bind:innerWidth={screenWidth} />

<div class="h-screen w-screen flex flex-col md:flex-row overflow-hidden">
    <nav class="
        {$navOpen ? 'w-64 translate-x-0' : 'w-0 -translate-x-full md:w-20 md:translate-x-0'} 
        lg:w-64 fixed md:relative z-50 h-full bg-[#0d0f14] border-r border-white/5 
        transition-all duration-300 ease-in-out flex flex-col"
    >
        <div class="p-8 hidden lg:block">
            <h1 class="text-2xl font-black text-dark-accent tracking-tighter">SPARK<span class="text-white">.</span></h1>
        </div>

        <div class="flex-1 flex flex-col gap-1 px-3 pt-4 overflow-y-auto no-scrollbar">
            {#each pages as pageItem}
                <NavButton
                    {...pageItem}
                    type={pageItem.icon}
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
                    <p class="text-[10px] uppercase tracking-[0.2em] text-gray-500 font-bold">Groups</p>
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
    </nav>

    <main class="flex-1 overflow-y-auto relative">
        <div class="fixed top-0 right-0 w-[500px] h-[500px] bg-dark-accent/5 blur-[120px] rounded-full pointer-events-none -z-10"></div>
        <slot />
    </main>
</div>