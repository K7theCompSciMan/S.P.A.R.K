<script lang="ts">
	import { goto } from '$app/navigation';
	import { NAV_ICONS, resolveNavIconKey } from './navButtonIcons';

	export let url: string;
	export let name: string;
	export let classModifier = '';
	export let type = '';
	export let selected = false;
	export let compact = false;
	export let onclick: () => void = () => goto(url);

	$: iconKey = resolveNavIconKey(type, name);
	$: iconMarkup = NAV_ICONS[iconKey];
</script>

<button
	class="flex items-center gap-3 px-3 py-2.5 w-full rounded-lg
		transition-all duration-200 group
		{selected ? 'bg-dark-background-500 text-dark-primary shadow-md' : 'text-dark-text hover:bg-dark-background-500 hover:text-dark-primary'}
		{compact ? 'justify-center' : ''}
		{classModifier}"
	on:click={onclick}
	title={compact ? name : ''}
>
	{@html iconMarkup}

	{#if !compact}
		<span class="truncate text-sm font-medium">{name}</span>
	{/if}
</button>
