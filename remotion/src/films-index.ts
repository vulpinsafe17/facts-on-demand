// Entry point for the long-form fact films only (no shorts, no Google-font loading):
// npx remotion render src/films-index.ts <Id> out.mp4
import { registerRoot } from 'remotion';
import { FilmsRoot } from './FilmsRoot';
registerRoot(FilmsRoot);
