Development browser pilot at implementation 40548dd. Actual comparison form
requests for f7e8n and f7f8q, table readings, desktop/mobile screenshots and
export Blob inspection succeeded; video/server capture reported zero errors.
The first start used --output without a matching proofshot.config.json. That
ProofShot version did not discover its session for later exec/stop calls, so the
exec timeline was absent and screenshots were copied into the session directory
before bundling. A matching local config restored stop/bundle. Final delivery
verification uses a config before start and repeats the interactions with a
complete command timeline. This pilot is not the final acceptance UI receipt.
