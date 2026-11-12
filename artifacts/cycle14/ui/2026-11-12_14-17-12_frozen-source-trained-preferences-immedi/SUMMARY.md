# ProofShot Verification Report

**Date:** 2026-11-12 14:26:52
**Project:** pln-chess-cycle6-delivery
**Dev Server:** PLN_CHESS_ROOT=/data/pln-chess-cycle14-final PYTHONPATH=/data/pln-chess-cycle14-final/src:/data/pln-chess-cycle14-final C14_OUT=/data/pln-chess-cycle6-delivery/artifacts/cycle14 C14_PROOF_STORE=/data/pln-chess-cycle14-final/.runtime/c14-trained-inspector.sqlite /data/pln-chess-cycle14-final/.venv/bin/python -u -m pln_chess serve --port 8794 2>&1 | tee --output-error=warn-nopipe /data/pln-chess-cycle6-delivery/artifacts/cycle14/ui/server-trained-final.log on localhost:8794

## What Was Verified

Frozen-source trained preferences: immediate evidence, empty-evidence retraction, supplied continuations, desktop and mobile, real archive upload/download reconstruction, and durable restart retrieval

## Video Recording

Full session recording: [session.webm](./session.webm) (526s)

## Screenshots

![empty-evidence-mobile.png](./empty-evidence-mobile.png)

![exact-reconstruction-mobile.png](./exact-reconstruction-mobile.png)

![proof-pagination-mobile.png](./proof-pagination-mobile.png)

![trained-desktop-ready.png](./trained-desktop-ready.png)

![trained-immediate-desktop.png](./trained-immediate-desktop.png)

![trained-three-ply-desktop.png](./trained-three-ply-desktop.png)

![trained-three-ply-final-desktop.png](./trained-three-ply-final-desktop.png)

![trained-two-ply-mobile.png](./trained-two-ply-mobile.png)

## Console Errors

No console errors detected.

## Server Errors

No server errors detected.

## Environment
- Browser: Chromium (headless)
- Viewport: 1280x720
- Duration: 526 seconds
