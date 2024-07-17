<script lang="ts">
	import { goto } from "$app/navigation";
	import { page } from "$app/stores";
	import { deviceData } from "$lib/stores";
	import type { Group } from "$lib/xata";
    let groups: Group[];
    $: groups = $page.data.groups;
    let disabled=true;
    let selectedGroup: Group | null;
    $: disabled = selectedGroup === null;
    function handleContinue(){
        if(selectedGroup){
            deviceData.set({assignedGroup: selectedGroup.id, assignedUser: $page.data.user.id, ...$deviceData});
        }
    }
</script>
<svelte:head>
    <title>Select Group</title>
</svelte:head>
<div class="text-center h-1/2 top-1/4 relative w-1/2 left-1/4 flex  flex-col justify-items-center text-amber-600 ">
    <h1 class="text-6xl mt-[4%]">
        Select a Group 
    </h1>
    <div class="overflow-scroll w-full h-96 flex flex-col">
        {#each groups as group}
            <!-- svelte-ignore a11y_click_events_have_key_events -->
            <!-- svelte-ignore a11y_no_static_element_interactions -->
            <div class="border {selectedGroup === group ? "border-emerald-700" : ""} bg-gray-500 mt-[3%] h-[12%] w-[75%] relative left-[12.5%] flex align-middle rounded-xl cursor-pointer" on:click={()=> {if(selectedGroup === group) {selectedGroup = null} else {selectedGroup = group}}}>
                <h2 class="text-xl w-[80%] h-fit text-ellipsis overflow-auto text-left absolute top-[17%] ml-[2%]">
                    {group.name}
                </h2>
                <p class="text-xl absolute right-[2%] top-[17%] ">
                    {group.devices["server"].length ===1 ? "1 server  | " : group.devices["server"].length + " servers | "} 
                    {group.devices["client"].length ===1 ? "1 client " : group.devices["client"].length + " clients "}
                </p>
            </div>
        {/each}
    </div>
    <button on:click={() =>  goto("/group-info")}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-8 absolute bottom-0 left-[23%]">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>  
    </button>
    <button on:click={() =>  handleContinue()} {disabled}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke={disabled ? "gray" : "currentColor"} class="size-8 absolute bottom-0 left-[67%]">
            <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
        </svg>
    </button>
</div>