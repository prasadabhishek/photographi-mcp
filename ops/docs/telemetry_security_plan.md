# Open-Source Telemetry Security Plan

Secure the telemetry system for open-source distribution by removing hardcoded secrets and using a Proxy/Relay architecture.

## The Problem
Hardcoding an `Authorization: Bearer <TOKEN>` in public source code allows anyone to:
1.  Flood your Axiom dataset with junk data.
2.  Exhaust your ingest limits.
3.  Spoof metrics (maliciously skewing your data).

## Proposed Solution: The Telemetry Relay
We will move the secret token to a tiny, free "Proxy" server (like a Cloudflare Worker).

### High-Level Flow
1.  **MCP Tool**: Hits `https://telemetry.your-domain.com/ingest` (NO token needed).
2.  **Relay (Proxy)**: Receives the JSON, adds the secret Axiom Token, and forwards it to Axiom.
3.  **Axiom**: Receives the data securely.

### Benefits
-   **Public Source Safety**: The secret token stays in your Private Cloudflare/Vercel environment.
-   **Rate Limiting**: You can add rate-limiting to the proxy to prevent spam.
-   **Validation**: The proxy can verify the shape of the JSON before sending it to Axiom.

## Proposed Changes

### 📡 Telemetry Engine

#### [MODIFY] [analytics.py](file:///Users/abhishekprasad/workspace/photographi/analytics.py)
- Change `official_endpoint` to the Proxy URL.
- REMOVE `official_token` from the source code.
- Update `transmit_telemetry` to not send the Authorization header (the proxy will add it).

---

### ☁️ Infrastructure (New)

#### [NEW] [telemetry_relay.js](file:///Users/abhishekprasad/workspace/photographi/docs/telemetry_relay.js)
- Provide a Cloudflare Worker script that handles the forwarding logic.

## Verification Plan

### Manual Verification
- Deploy the relay.
- Point `analytics.py` to the new relay endpoint.
- Verify data still reaches Axiom without the secret token in the local code.
