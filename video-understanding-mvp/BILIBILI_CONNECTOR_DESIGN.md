# Bilibili Connector Design

## Goal
Define a stable, product-oriented connector layer for Bilibili video understanding.

The core idea is:
- do **not** bind the product to brittle scraping logic
- separate **content acquisition** from **understanding**
- support both offline video analysis and future live/real-time observation

---

## Design principles

1. **Connector layer and understanding layer are separate**
2. **Browser-observable content is a first-class source**
3. **Local file fallback always exists**
4. **Offline first, live later**
5. **Connector outputs a normalized media session contract**

---

## Unified connector contract

Every connector should normalize into a structure like:

```json
{
  "source": "bilibili",
  "mode": "offline|browser_session|live_window",
  "title": "video title",
  "video_path": "/local/path/or/null",
  "audio_path": "/local/path/or/null",
  "metadata": {},
  "subtitle_path": null,
  "danmaku_path": null,
  "web_url": "https://...",
  "session_id": "optional"
}
```

This lets the understanding engine ignore how the content was acquired.

---

## Connector types

### 1. LocalFileConnector
**Purpose:** process already-downloaded local media

Input:
- local video path

Output:
- normalized local media session

Use cases:
- testing
- manual ingest
- fallback when Bilibili acquisition fails

---

### 2. BilibiliURLConnector
**Purpose:** ingest a Bilibili video URL into local media

Input:
- Bilibili URL / BV link

Acquisition strategy:
- first practical path: `yt-dlp`
- later optional paths:
  - browser-assisted authenticated download
  - subtitle and metadata extraction

Output:
- local video file path
- metadata json
- optional subtitle/danmaku files

Use cases:
- offline video understanding
- batch ingest pipeline

---

### 3. BrowserSessionConnector
**Purpose:** use a logged-in user browser session as the observation surface

Input:
- active browser tab or dedicated automation browser session

Capabilities:
- read page title / description / visible metadata
- monitor player state
- assist extraction of visible subtitles / metadata / comments
- later support live-page observation

Output:
- normalized browser-backed media session

Use cases:
- pages that are easier to access with a real browser session
- user-visible / user-authorized content access
- transition path toward live observation

---

### 4. LiveObservationConnector
**Purpose:** observe a currently playing/live Bilibili session in rolling windows

Input:
- browser session or stream capture session

Window outputs:
- rolling audio chunk
- rolling frame set
- rolling metadata snapshot
- rolling danmaku/comment snapshot if available

Output mode:
- `live_window`

Use cases:
- near-real-time summary
- topic shift detection
- event/highlight alerts

---

### 5. RecordingConnector
**Purpose:** analyze a captured live recording later

Input:
- recorded stream file

Output:
- same as LocalFileConnector

Use cases:
- compliance-safe live replay analysis
- delayed processing

---

## Recommended implementation order

### Phase 1
- LocalFileConnector
- BilibiliURLConnector

### Phase 2
- BrowserSessionConnector

### Phase 3
- LiveObservationConnector
- RecordingConnector

---

## Product path

### Offline MVP
```text
Bilibili URL -> local media -> ASR/OCR/fusion -> summary/chapters/timeline
```

### Browser-assisted offline mode
```text
Browser tab -> metadata/session -> optional capture/download -> local media -> understanding
```

### Quasi-real-time live mode
```text
Live browser session -> rolling 30s audio/frame windows -> rolling summaries -> session memory
```

### Full multi-agent future
```text
Connector -> event bus -> speech agent / vision agent / fusion agent / planner / critic
```

---

## Why this is better than anti-bot-centric design

Because the real product goal is not "scrape Bilibili pages".
The goal is:
- observe videos the user can access
- acquire usable audio/video/text context
- run understanding reliably

This connector-first design is more stable, more maintainable, and easier to evolve into a live multi-agent product.
