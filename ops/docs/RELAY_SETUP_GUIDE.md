# ☁️ Cloudflare Worker Relay Setup Guide

Follow these steps to securely deploy your telemetry relay. This ensures your **Axiom Token** stays private even when the `photographi` source code is public.

### 1. Create the Worker
1.  Log in to your [Cloudflare Dashboard](https://dash.cloudflare.com/).
2.  In the left sidebar, click **"Workers & Pages"**.
3.  Click the blue **"Create application"** button.
4.  Click **"Create Worker"**.
5.  **Give it a name**: e.g., `photographi-telemetry`.
6.  Click **"Deploy"**.

### 2. Add the Code
1.  On the confirmation page, click **"Edit Code"**.
2.  In the editor, delete all existing code in `worker.js`.
3.  Open [telemetry_relay.js](file:///Users/abhishekprasad/workspace/photographi/docs/telemetry_relay.js) on your computer.
4.  Copy the entire content and paste it into the Cloudflare editor.
5.  Click **"Deploy"** (top right).

### 3. Add your Secret Token
1.  Go back to the main page for your Worker (click the name at the top left).
2.  Click the **"Settings"** tab.
3.  Click **"Variables"** in the left sub-menu.
4.  Under **"Environment Variables"**, click **"Add variable"**.
5.  **Variable Name**: `AXIOM_TOKEN`
6.  **Value**: `xaat-ac4294b3-9d53-468f-915a-ee3b1ba62496`
7.  Click the **"Encrypt"** button (to hide the token).
8.  Click **"Save and deploy"**.

### 4. Finish the Link
1.  Copy your **Worker URL** from the top of the summary page (it looks like `https://photographi-telemetry.yourname.workers.dev`).
2.  Paste that URL into [analytics.py](file:///Users/abhishekprasad/workspace/photographi/analytics.py) on **Line 21**:
    ```python
    self.official_relay = "YOUR_WORKER_URL_HERE"
    ```

---
**Done!** Your metrics are now flowing securely through your own private proxy. 🛡️🚀
