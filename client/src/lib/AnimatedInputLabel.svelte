<script lang="ts">
  export let type = "text";
  export let width = "w-full";
  export let height = ""; // Prop placeholder for legacy compatibility
  export let name = "";
  export let labelbg = ""; // Prop placeholder for legacy compatibility
  export let value = "";
  export let size = "";
</script>

<div class="relative group {width} {size}">
  <input 
    {type} 
    id={name}
    bind:value 
    placeholder=" "
    class="block w-full px-4 pt-6 pb-2 text-sm text-zinc-100 bg-dark-background-950/40 border border-white/[0.07] rounded-xl appearance-none focus:outline-none focus:ring-0 focus:border-dark-primary peer transition-all duration-200"
  />
  <label 
    for={name} 
    class="absolute text-sm text-zinc-500 duration-200 transform -translate-y-3 scale-75 top-4 z-10 origin-[0] left-4 peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-3 peer-focus:text-dark-primary pointer-events-none font-medium"
  >
    {name}
  </label>
</div>