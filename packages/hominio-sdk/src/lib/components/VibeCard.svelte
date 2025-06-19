<script>
	export let vibe;
</script>

<div class="vibe-card">
	<h3>{vibe.displayName}</h3>
	<p>{vibe.description}</p>
	<span>Version: {vibe.version}</span>
</div>

<style>
	.vibe-card {
		border: 1px solid #ccc;
		border-radius: 8px;
		padding: 16px;
		margin: 8px;
	}
</style>
