<script lang='ts'>
	import type { PublicUser } from "$lib";
	import AnimatedInputLabel from "./AnimatedInputLabel.svelte";
	import type { User } from "./xata";

    export let user: PublicUser;
</script>   

<div class='bg-dark-background-500 w-[25%] h-[25%] rounded-2xl text-dark-text p-[1%] px-[2%]'>
    <h1 class="text-xl text-dark-secondary text-center">User Settings</h1>
    <AnimatedInputLabel name="Username" labelbg="bg-dark-background-500" bind:value={user.username } size="scale-110" />
</div>