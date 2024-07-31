<script lang="ts">
	import { onMount } from "svelte";
    import { initStore } from "$lib/tauri";
    import "../../app.css";
    onMount(async() => {
        await initStore();
    })
</script>
<div class="bg-gradient-to-br from-sky-700 to-indigo-900 overflow-auto h-screen w-full">
    <slot/>
</div>