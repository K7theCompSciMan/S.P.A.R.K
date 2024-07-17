<script lang="ts">
	import { page } from "$app/stores";
	import { redirect } from "@sveltejs/kit";

    $: if($page.data.user && $page.data.device) {
        console.log("User and device are set, redirecting to dashboard");
        throw redirect(300, "/dashboard");
    } else {
        throw redirect(300, "/setup");
    }
</script>