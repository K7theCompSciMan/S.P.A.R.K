<script lang="ts">
	import { goto } from "$app/navigation";


</script>

<svelte:head>
    <title>Welcome to S.P.A.R.K</title>
</svelte:head>

<div class="text-center h-1/2 top-1/4 relative w-1/2 left-1/4 flex  flex-col justify-items-center text-amber-600">
    <h1 class="text-6xl mt-[4%]">
        Welcome to S.P.A.R.K!
    </h1>
    <p class="text-2xl mt-[4%]  w-[75%] left-[12.5%] relative">
        Once you've downloaded SPARK, you'll see pages like this to help guide you through your setup. 
        <br>
        If you've already set up SPARK, then log in and check out your <b> admin dashboard</b>
    </p>
    <button disabled>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="gray" class="size-8 absolute bottom-1/4 left-[23%]">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>  
    </button>
    <button on:click={() =>  goto("/login")}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-8 absolute bottom-1/4 left-[67%]">
            <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
        </svg>
    </button>
</div>