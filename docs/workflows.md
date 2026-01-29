# Workflows: Unleashing Visual Intelligence

Because `photographi` is an engine, it supports multiple high-value workflows for photographers and archivists.

---

## 🔍 1. Semantic Search (The "Google Photos" Experience)
**Goal**: Query your local library using natural language without uploading to the cloud.

**Setup**:
1.  Connect `photographi` as an MCP Server to Claude Desktop or Gemini.
2.  Ensure your folder is accessible.

**Use Cases**:
*   **Finding Specific Shots**: "Find me a sharp, well-exposed photo of a dog running in the 'Summer2024' folder."
*   **Technical Queries**: "Show me all photos taken at ISO > 6400 that are still usable."
*   **Subject Filtering**: "Find me all portraits where the person is in focus."

---

## 📊 2. Library Auditing (Data-Driven Photography)
**Goal**: Improve your photography skills by analyzing your technical performance over time.

**Command**:
```bash
python server.py --analyze /path/to/year_archive > report.json
```

**Insights**:
*   **Lens Performance**: Correlate *Sharpness Scores* with *Lens Metadata*. Which lens gives you the crispest results?
*   **Handheld Limits**: Analyze *Exposure Scores* vs *Shutter Speed*. At what speed do your shots start getting blurry?
*   **Keeper Rate**: What percentage of your shots are technically "Good" (> 0.7)?

---

## 🧹 3. Professional Culling (Lightroom Integration)
**Goal**: Automate the tedious process of rejecting bad photos.

**The Flow**:
1.  **Ingest**: Import RAW photos to your drive.
2.  **Analyzes**: Run the `cull` command mode:
    ```bash
    python server.py --cull /path/to/photos --threshold 0.4 --mode xmp
    ```
3.  **Sync**: Open Lightroom. The engine has already marked technically flawed images as "Rejected" (standard XMP tag).
4.  **Review**: Filter by "Rejected". Quickly verify and delete.
5.  **Edit**: You are left with only the technically sound images, ready for creative editing.

---

## 🤖 4. Agentic Editing (Future)
**Goal**: AI Agents that can edit for you.

*   **Concept**: An agent uses `photographi` to find the best photo, then uses a hypothetical editing tool to apply a preset.
*   **State**: *Experimental*. The "Vision" part is ready (finding the photo); the "Editing" part is on the roadmap.
