<script lang="ts">
	import { goto } from "$app/navigation";
	import type { Device, PublicUser } from "$lib";
	import { deviceData } from "$lib/stores";
	import { getStore, setStore } from "$lib/tauri";
	import type { Group } from "$lib/xata";
	import { onMount } from "svelte";
    let groups: Group[];
    let disabled=true;
    let selectedGroup: Group | null = null;
    $: disabled = (selectedGroup === null);
    let value = "";
    let user: PublicUser;
    let accessToken: string;

    onMount(async () => {
        user = await getStore("user") as PublicUser;
        if(!user) {
            goto("/login");
        }
        let device = await getStore("device") as Device;
        if(device.id  && device.assignedUser){
            goto("/dashboard");
        }

        accessToken = await getStore("accessToken") as string;

        const res = await fetch(`https://spark-api.fly.dev/groups/${user.id}`, {
            method: 'GET',
            headers: {
                authorization: `Bearer ${accessToken}`
            }
        });
        if(res.status === 200){
            groups = await res.json();
        }
        else {
            console.error(await res.text());
        }
    })

    async function handleContinue(){
        if(selectedGroup){
            deviceData.set({assignedGroup: selectedGroup.id, assignedUser: {id:user.id}, ...$deviceData});
            await setStore("group", selectedGroup);
            goto("/device-info");
        }
    }
    async function deleteGroup(group: Group){
        const res = await fetch(`https://spark-api.fly.dev/group/${group.id}`, {
            method: "DELETE",
            headers: {
                authorization: `Bearer ${accessToken}`
            },         
        })

        if(res.ok){
            console.log("deleted")
            groups = groups.filter(g => g !== group);
        }
        else{
            console.error(await res.text())
        }
    }
    async function handleSubmit(name: string){
        createGroupPopup = false;
        groupCreated = true;
        value="";
        const res = await fetch("https://spark-api.fly.dev/group", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                authorization: `Bearer ${accessToken}`
            },
            body: JSON.stringify({name})
        });
        if(res.ok){
            const data = await res.json();
            groups = [...groups, data];
            selectedGroup = data;
        }
        else{
            console.error(await res.text())
        }
    }
    let createGroupPopup=false;
    $: (createGroupPopup &&!value) ?  document.getElementById("createGroupInput")!.focus() : null;
    let groupCreated = false;
</script>
<svelte:head>
    <title>Select Group</title>
</svelte:head>
<div class="text-center h-1/2 top-1/4 relative w-1/2 left-1/4 flex  flex-col justify-items-center text-amber-600 ">
    <h1 class="text-6xl mt-[4%]">
        Select a Group 
    </h1>
    <div class="overflow-scroll w-full h-96 mt-[1%] ">
        {#each groups as group}
        <div class="border {selectedGroup === group ? "border-emerald-700 border-2 bg-gray-200 scale-105" : "bg-gray-500"}  mt-[2%] h-[12%] w-[75%] relative left-[12.5%] flex align-middle rounded-xl cursor-pointer shadow-xl hover:bg-gray-200 hover:scale-105 transition-all delay-75 duration-150 " >
                <!-- svelte-ignore a11y_click_events_have_key_events -->
                <!-- svelte-ignore a11y_no_static_element_interactions -->
                <div on:click={()=> {if(selectedGroup === group) {selectedGroup = null} else {selectedGroup = group}}}>
                <h2 class="text-xl w-[80%] h-fit text-ellipsis overflow-auto text-left absolute top-[17%] ml-[2%]">
                    {group.name}
                </h2>
                <p class="text-xl absolute right-[8%] top-[17%]">
                    {group.devices["server"].length ===1 ? "1 server  | " : group.devices["server"].length + " servers | "} 
                    {group.devices["client"].length ===1 ? "1 client " : group.devices["client"].length + " clients "}
                </p></div>
                <button on:click={async () => await deleteGroup(group)}>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6 absolute right-[2%] top-[21%] transition hover:stroke-red-900 ">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                    </svg>                      
                </button>
            </div>
        {/each}
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <!-- svelte-ignore a11y_click_events_have_key_events -->
        <div class=" bg-transparent mt-[2%] h-[12%] w-[75%] relative left-[12.5%] flex align-middle rounded-xl cursor-pointer group {createGroupPopup ? "hidden" : ""} " id="add" on:click={()=>{createGroupPopup = true; setTimeout(()=> document.getElementById("createGroupInput")?.focus(), 100)}}>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" id="add" class="size-6 absolute top-[24%] group-hover:rotate-45 group-hover:stroke-gray-500 transition-all group-hover:scale-110 duration-100 delay-75 ">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            <h2 class="text-xl w-[80%] h-fit text-ellipsis overflow-auto text-left absolute top-[17%] ml-[2%] left-[2.5%] group-hover:text-gray-500 transition-all group-hover:scale-110 group-hover:left-[7.5%] duration-100 delay-75 ">
                Create a New Group
            </h2>
        </div>
        <div class="border border-emerald-700 bg-gray-500 mt-[2%] h-[12%] w-[75%] relative left-[12.5%] flex align-middle rounded-xl cursor-pointer shadow-xl {createGroupPopup ? "" : "hidden"} " >
            <input type="text" id="createGroupInput" placeholder="Enter a Name" name="Create New Event" class="pl-[2%] bg-transparent w-full text-xl focus:outline-none " bind:value on:keypress={async (event) => {if(event.key === "Enter" && !groupCreated) {await handleSubmit(value)}}} on:focusout={async () => {if(!value) {createGroupPopup = false} else if (!groupCreated && createGroupPopup) {await handleSubmit(value)}}}>
        </div>
    </div>
    <button on:click={() =>  goto("/group-info")}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-8 absolute bottom-0 left-[23%]">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>  
    </button>
    <button on:click={async () => await handleContinue()} {disabled}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke={disabled ? "gray" : "currentColor"} class="size-8 absolute bottom-0 left-[67%]">
            <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
        </svg>
    </button>
</div>