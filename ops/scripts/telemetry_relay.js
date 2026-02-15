/**
 * Telemetry Relay for photographi MCP
 * 
 * Deploy this to Cloudflare Workers to hide your Axiom token.
 */

export default {
    async fetch(request, env, ctx) {
        // 1. Only allow POST requests
        if (request.method !== "POST") {
            return new Response("Method Not Allowed", { status: 405 });
        }

        try {
            // 2. Read the incoming telemetry payload
            const payload = await request.json();

            // 3. Forward to Axiom with the SECRET token (stored in env.AXIOM_TOKEN)
            const axiomResponse = await fetch("https://api.axiom.co/v1/datasets/photographi-mcp/ingest", {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${env.AXIOM_TOKEN}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            // 4. Return the result back to the MCP tool
            return new Response("OK", { status: axiomResponse.status });

        } catch (err) {
            return new Response("Internal Error", { status: 500 });
        }
    },
};
