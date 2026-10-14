<script lang="ts">
  import AnimatedInputLabel from '$lib/AnimatedInputLabel.svelte';
  import { goto } from '$app/navigation';
  import { getStore, setStore } from '$lib/tauri';
  import { onMount } from 'svelte';
  import type { Device } from '$lib';
  import { loginApi } from '$lib/api';
  import { restoreAuthFromStore } from '$lib/auth';
  import { isPublicUserReady } from '$lib/storeAccess';

  let canProceed = false;
  let email = '';
  let password = '';
  let errorMsg = '';

  onMount(async () => {
    await restoreAuthFromStore();

    const u = await getStore('user');
    const device = (await getStore('device')) as Device;
    if (device?.id && device?.assignedUser) {
      await goto('/dashboard');
      return;
    }
    if (isPublicUserReady(u)) {
      canProceed = true;
      await goto('/group-info');
    }
  });

  async function handleSubmit() {
    errorMsg = '';
    const response = await loginApi(email, password);
    if (response.status !== 200) {
      const body = await response.json().catch(() => ({}));
      errorMsg = body.error ?? 'Invalid credentials. Please try again.';
      return false;
    }

    const data = await response.json();
    const { user: u, accessToken, refreshToken } = data;
    await setStore('user', u);
    await setStore('accessToken', accessToken);
    await setStore('refreshToken', refreshToken);

    canProceed = true;
    return true;
  }

  let peek = false;
</script>

<svelte:head>
  <title>Log in • SPARK</title>
</svelte:head>

<div class="flex flex-col items-center justify-center min-h-screen p-4 bg-dark-background-950 relative overflow-hidden">
  <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(99,102,241,0.05),transparent_65%)] pointer-events-none"></div>

  <div class="spark-card p-8 md:p-12 w-full max-w-md flex flex-col items-center text-center gap-6 border border-white/[0.05]">
    <div>
      <h1 class="text-3xl font-bold text-white tracking-tight mb-2">Welcome Back</h1>
      <p class="text-sm text-zinc-400">
        New here? <a href="/register" class="font-medium text-dark-primary hover:text-dark-accent transition-colors">Create an account</a>
      </p>
    </div>

    {#if errorMsg}
      <div class="w-full bg-red-500/10 border border-red-500/20 text-red-400 text-xs py-2.5 px-3 rounded-xl text-left">
        {errorMsg}
      </div>
    {/if}

    <div class="w-full flex flex-col gap-4 relative">
      <AnimatedInputLabel name="Email" type="email" bind:value={email} />

      <div class="relative w-full">
        <AnimatedInputLabel name="Password" type={peek ? 'text' : 'password'} bind:value={password} />
        <button
          type="button"
          class="absolute right-4 top-[35%] text-zinc-500 hover:text-white transition-colors"
          on:click={() => { peek = !peek; }}
          aria-label={peek ? 'Hide password' : 'Show password'}
        >
          {#if !peek}
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" />
            </svg>
          {:else}
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
            </svg>
          {/if}
        </button>
      </div>

      <button type="button" class="spark-btn-primary w-full mt-2" on:click={async () => await handleSubmit()}>
        Log In
      </button>
    </div>

    <div class="flex gap-6 items-center justify-between w-full pt-4 border-t border-white/[0.05] mt-2">
      <button type="button" class="text-zinc-500 text-xs font-medium hover:text-white transition-colors" on:click={() => goto('/setup')}>
        &larr; Back
      </button>
      <button type="button" class="text-dark-primary font-semibold text-xs hover:text-dark-accent transition-colors disabled:opacity-30" disabled={!canProceed} on:click={() => goto('/group-info')}>
        Next &rarr;
      </button>
    </div>
  </div>
</div>
