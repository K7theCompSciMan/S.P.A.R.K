<script lang="ts">
    export let type="text";
    export let width="w-[75%]";
    export let height="h-8";
    export let name="";
    export let labelbg = "";
    export let value = "";
    let isfocused=false;
    export let size = "";
</script>

{#if value && !isfocused}
<div class=" h-fit self-center flex mt-[6%] {width} {size}">
    <input {type} class="rounded-xl {width} self-center bg-transparent border {height} w-full focus peer pl-2" id={name} bind:value on:focusin={() => isfocused=true} on:focusout={() => isfocused=false}>
    <label for={name} id="{name}-label" class=" pl-2 pr-2 rounded-md absolute ml-2 mt-1 cursor-text transform transition-transform {labelbg} -translate-y-[1.125rem] text-md">{name}</label> 
</div>
{:else}
<div class=" h-fit self-center flex mt-[6%] {width} {size}">
    <input {type} class="rounded-xl {width} self-center bg-transparent border {height} w-full focus peer pl-2" id={name} bind:value on:focusin={() => isfocused=true} on:focusout={() => isfocused=false}>
    <label for={name} id="{name}-label" class=" pl-2 pr-2 rounded-md absolute ml-2 mt-1 cursor-text transform transition-all {labelbg} peer-focus:-translate-y-[1.125rem] peer-focus:text-md">{name}</label> 
</div>
{/if}