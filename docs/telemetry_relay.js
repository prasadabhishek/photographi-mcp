/**
 * ☁️ photographi Telemetry Relay (Cloudflare Worker)
 * 
 * This script is designed to run on **Cloudflare Workers**, not your local machine.
 * It strictly proxies telemetry data to Axiom so your API Token remains private.
 * 
 * --- SETUP GUIDANCE ---
 * 
 * 1. Create a Worker:
 *    - Go to https://dash.cloudflare.com/ -> Workers & Pages -> Create Worker.
 *    - Name it `photographi-telemetry`.
 * 
 * 2. Deploy this Code:
 *    - Click "Edit Code" in the dashboard.
 *    - Paste the contents of this file into `worker.js`.
 *    - Click "Deploy".
 * 
 * 3. Configure Secrets (No .env file needed!):
 *    - Go to your Worker's Settings -> Variables.
 *    - Add `AXIOM_TOKEN` as an Encrypted Variable (Value: Your Axiom Ingest Token).
 *    - (Optional) Add `AXIOM_DATASET` (Default: "photographi-telemetry").
 *    - **Note**: The `env` object in the code below is automatically injected by Cloudflare 
 *      at runtime. It reads these variables securely.
 * 
 * 4. Connect CLI:
 *    - Copy your Worker's URL (e.g., https://photographi-telemetry.user.workers.dev).
 *    - Pass it to the server: `python server.py --telemetry-endpoint YOUR_WORKER_URL`
 */

export default {
    async fetch(request, env) {
        // 1. Handle CORS (Allow all origins for local tool usage)
        if (request.method === "OPTIONS") {
            return new Response(null, {
                headers: {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                },
            });
        }

        // 2. Only allow POST
        if (request.method !== "POST") {
            return new Response("Method Not Allowed", { status: 405 });
        }

        // 3. Validate Token Existence
        if (!env.AXIOM_TOKEN) {
            return new Response("Server Misconfiguration: Missing AXIOM_TOKEN", { status: 500 });
        }

        try {
            const payload = await request.json();
            const dataset = env.AXIOM_DATASET || "photographi-telemetry";

            // 4. Forward to Axiom
            const axiomResponse = await fetch(`https://api.axiom.co/v1/datasets/${dataset}/ingest`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${env.AXIOM_TOKEN}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            // 5. Return Axiom's response
            const responseBody = await axiomResponse.text();
            return new Response(responseBody, {
                status: axiomResponse.status,
                headers: {
                    "Access-Control-Allow-Origin": "*",
                    "Content-Type": "application/json",
                },
            });

        } catch (err) {
            return new Response(JSON.stringify({ error: err.message }), {
                status: 500,
                headers: { "Access-Control-Allow-Origin": "*" },
            });
        }
    },
};
