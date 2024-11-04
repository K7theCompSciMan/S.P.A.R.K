<script lang="ts">
	import { goto } from "$app/navigation";
</script>
<div class="text-center h-1/2 top-1/4 relative w-1/2 left-1/4 flex  flex-col justify-items-center text-amber-600">
    <h1 class="text-6xl mt-[4%]">
        Choose a group for your device to connect to!
    </h1>
    <p class="text-2xl mt-[4%]  w-[75%] left-[12.5%] relative">
        Groups are basically collections of devices (either clients or servers) that your S.P.A.R.K AI interacts with    
    </p>
    <button on:click={() =>  goto("/setup")}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-8 absolute bottom-1/4 left-[23%]">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>  
    </button>
    <button on:click={() =>  goto("/groups")}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-8 absolute bottom-1/4 left-[67%]">
            <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
        </svg>
    </button>
</div>