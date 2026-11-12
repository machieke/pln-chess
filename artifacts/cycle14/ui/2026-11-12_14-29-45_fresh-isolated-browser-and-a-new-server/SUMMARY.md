# ProofShot Verification Report

**Date:** 2026-11-12 14:35:33
**Project:** pln-chess-cycle6-delivery
**Dev Server:** PLN_CHESS_ROOT=/data/pln-chess-cycle14-final PYTHONPATH=/data/pln-chess-cycle14-final/src:/data/pln-chess-cycle14-final C14_OUT=/data/pln-chess-cycle6-delivery/artifacts/cycle14 C14_PROOF_STORE=/data/pln-chess-cycle14-final/.runtime/c14-trained-inspector.sqlite /data/pln-chess-cycle14-final/.venv/bin/python -u -m pln_chess serve --port 8794 2>&1 | tee --output-error=warn-nopipe /data/pln-chess-cycle6-delivery/artifacts/cycle14/ui/server-trained-restart-verified.log on localhost:8794

## What Was Verified

Fresh isolated browser and a new server process retrieve the trained native proof from the retained durable store

## Video Recording

Full session recording: [session.webm](./session.webm) (337s)

## Screenshots

![restored-trained-proof-desktop.png](./restored-trained-proof-desktop.png)

![restored-trained-proof-mobile.png](./restored-trained-proof-mobile.png)

## Console Errors

No console errors detected.

## Server Errors

No server errors detected.

## Environment
- Browser: Chromium (headless)
- Viewport: 1280x720
- Duration: 337 seconds
