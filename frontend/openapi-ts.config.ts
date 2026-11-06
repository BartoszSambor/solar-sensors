import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
	// Local stack: Caddy serves https://localhost with its own CA (see npm script).
	input: "https://localhost/api/v1/openapi.json",
	output: "./src/client",
	// throwOnError: HTTP errors reject the promise instead of returning { error }.
	plugins: [
		{
			name: "@hey-api/client-axios",
			// Same-origin requests (nginx proxies the API); no hard-coded host.
			baseUrl: false,
			throwOnError: true,
		},
	],
});
