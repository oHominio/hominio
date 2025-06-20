<script>
	import '../app.css';

	let { children } = $props();
</script>

<div class="hominio-app">
	{@render children()}
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		font-family:
			-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
		background: linear-gradient(135deg, #f5f1e8 0%, #ede7db 100%);
		color: #1e3a5f;
		min-height: 100vh;
	}

	.hominio-app {
		min-height: 100vh;
		background: linear-gradient(135deg, #f5f1e8 0%, #ede7db 100%);
	}

	:global(*) {
		box-sizing: border-box;
	}

	:global(::selection) {
		background: rgba(126, 212, 173, 0.3);
		color: #1e3a5f;
	}

	:global(::-webkit-scrollbar) {
		width: 8px;
		height: 8px;
	}

	:global(::-webkit-scrollbar-track) {
		background: rgba(30, 58, 95, 0.1);
		border-radius: 4px;
	}

	:global(::-webkit-scrollbar-thumb) {
		background: rgba(30, 58, 95, 0.3);
		border-radius: 4px;
	}

	:global(::-webkit-scrollbar-thumb:hover) {
		background: rgba(30, 58, 95, 0.5);
	}
</style>
