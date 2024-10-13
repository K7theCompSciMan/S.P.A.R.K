<script lang="ts">
	import type { Group } from '$lib/xata';
	import { goto } from "$app/navigation";
	import type { Device, PublicUser } from "$lib";
	import { getStore } from "$lib/tauri";
	import { onMount } from "svelte";

    let user: PublicUser;
    let group: Group;
    let device: Device;
    onMount(async () => {
        device = await getStore("device") as Device;
        user = await getStore("user") as PublicUser;
        
        if(!user) {
            goto("/login");
        }
    });

</script>
{#await user}
    <div class='text-dark-text'>Loading...</div>
{:then user}
    <h1 class='text-dark-text'>this is ur dashboard, {user.username}</h1>
{:catch error}
    <div class='text-dark-text'>{error.message}</div>
{/await}