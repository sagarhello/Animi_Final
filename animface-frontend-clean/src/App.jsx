import { useState, useEffect, useRef } from "react";

const style = `
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Nunito:wght@300;400;600;700&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  :root {
    --bg: #080b14;
    --surface: #0e1420;
    --surface2: #141a28;
    --border: #1e2d45;
    --accent: #00e5ff;
    --accent2: #ff2d78;
    --accent3: #a855f7;
    --text: #e8f0fe;
    --muted: #5a7090;
    --glow: 0 0 20px rgba(0,229,255,0.3);
    --glow2: 0 0 20px rgba(255,45,120,0.3);
  }

  body { background: var(--bg); color: var(--text); font-family: 'Nunito', sans-serif; }

  .app { min-height: 100vh; display: flex; flex-direction: column; overflow: hidden; }

  /* NAV */
  .nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 32px;
    background: rgba(8,11,20,0.9);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border);
    position: sticky; top: 0; z-index: 100;
  }
  .logo {
    font-family: 'Orbitron', sans-serif;
    font-size: 20px; font-weight: 900;
    background: linear-gradient(135deg, var(--accent), var(--accent3));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: 2px;
  }
  .logo span { color: var(--accent2); -webkit-text-fill-color: var(--accent2); }
  .nav-tabs { display: flex; gap: 4px; }
  .nav-tab {
    padding: 8px 20px; border-radius: 20px; border: none; cursor: pointer;
    font-family: 'Nunito', sans-serif; font-size: 13px; font-weight: 600;
    background: transparent; color: var(--muted);
    transition: all 0.2s;
  }
  .nav-tab:hover { color: var(--text); }
  .nav-tab.active {
    background: rgba(0,229,255,0.1);
    color: var(--accent);
    border: 1px solid rgba(0,229,255,0.3);
  }
  .nav-upload-btn {
    padding: 8px 20px; border-radius: 20px;
    background: linear-gradient(135deg, var(--accent2), var(--accent3));
    border: none; color: white; font-family: 'Nunito', sans-serif;
    font-size: 13px; font-weight: 700; cursor: pointer;
    box-shadow: var(--glow2); transition: transform 0.2s;
  }
  .nav-upload-btn:hover { transform: scale(1.05); }

  /* TABS CONTENT */
  .tab-content { flex: 1; }

  /* ========== FEED ========== */
  .feed-page { display: flex; gap: 0; min-height: calc(100vh - 65px); }
  .feed-sidebar {
    width: 240px; padding: 24px 16px;
    border-right: 1px solid var(--border);
    flex-shrink: 0;
  }
  .sidebar-section { margin-bottom: 32px; }
  .sidebar-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 10px; font-weight: 700; letter-spacing: 2px;
    color: var(--muted); text-transform: uppercase; margin-bottom: 12px;
  }
  .sidebar-item {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 12px; border-radius: 10px; cursor: pointer;
    font-size: 14px; font-weight: 600; color: var(--muted);
    transition: all 0.2s;
  }
  .sidebar-item:hover, .sidebar-item.active {
    background: var(--surface2); color: var(--text);
  }
  .sidebar-item.active { color: var(--accent); }
  .sidebar-icon { font-size: 18px; }

  .feed-main { flex: 1; padding: 24px; max-width: 680px; margin: 0 auto; }
  .feed-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
  .feed-title { font-family: 'Orbitron', sans-serif; font-size: 14px; color: var(--muted); letter-spacing: 1px; }

  /* STORY BAR */
  .story-bar { display: flex; gap: 16px; overflow-x: auto; padding-bottom: 8px; margin-bottom: 28px; }
  .story-bar::-webkit-scrollbar { height: 3px; }
  .story-bar::-webkit-scrollbar-track { background: transparent; }
  .story-bar::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
  .story-item { display: flex; flex-direction: column; align-items: center; gap: 6px; cursor: pointer; flex-shrink: 0; }
  .story-ring {
    width: 60px; height: 60px; border-radius: 50%;
    background: linear-gradient(135deg, var(--accent2), var(--accent3), var(--accent));
    padding: 2px; transition: transform 0.2s;
  }
  .story-ring:hover { transform: scale(1.1); }
  .story-avatar {
    width: 100%; height: 100%; border-radius: 50%;
    background: var(--surface); display: flex; align-items: center; justify-content: center;
    font-size: 22px; overflow: hidden;
  }
  .story-name { font-size: 11px; color: var(--muted); font-weight: 600; }
  .story-add .story-ring { background: var(--surface2); border: 2px dashed var(--border); padding: 0; }
  .story-add .story-avatar { font-size: 24px; color: var(--accent); }

  /* POST CARD */
  .post-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px; margin-bottom: 20px;
    overflow: hidden; transition: border-color 0.2s;
  }
  .post-card:hover { border-color: rgba(0,229,255,0.3); }
  .post-header { display: flex; align-items: center; gap: 12px; padding: 16px; }
  .post-avatar-wrap {
    width: 42px; height: 42px; border-radius: 50%;
    background: linear-gradient(135deg, var(--accent2), var(--accent3));
    padding: 2px; flex-shrink: 0;
  }
  .post-avatar {
    width: 100%; height: 100%; border-radius: 50%;
    background: var(--surface2); display: flex;
    align-items: center; justify-content: center; font-size: 20px;
  }
  .post-user-name { font-weight: 700; font-size: 14px; }
  .post-time { font-size: 12px; color: var(--muted); }
  .post-privacy-badge {
    margin-left: auto; padding: 4px 10px; border-radius: 12px;
    background: rgba(168,85,247,0.15); border: 1px solid rgba(168,85,247,0.3);
    font-size: 11px; font-weight: 700; color: var(--accent3);
  }

  /* VIDEO */
  .post-video {
    position: relative; aspect-ratio: 9/16; max-height: 400px;
    background: var(--surface2); overflow: hidden; cursor: pointer;
  }
  .anime-canvas {
    width: 100%; height: 100%;
    display: flex; align-items: center; justify-content: center;
    position: relative; overflow: hidden;
  }
  .anime-bg {
    position: absolute; inset: 0;
    background: linear-gradient(160deg, #0a0015 0%, #12002a 40%, #001a2e 100%);
  }
  .anime-scene { position: relative; z-index: 1; text-align: center; width: 100%; }
  .anime-char { font-size: 80px; animation: charBob 2s ease-in-out infinite; display: block; }
  @keyframes charBob {
    0%,100% { transform: translateY(0) rotate(-3deg); }
    50% { transform: translateY(-12px) rotate(3deg); }
  }
  .anime-sparkles { position: absolute; inset: 0; pointer-events: none; }
  .sparkle {
    position: absolute; font-size: 16px;
    animation: sparklePop 3s ease-in-out infinite;
  }
  @keyframes sparklePop {
    0%,100% { opacity: 0; transform: scale(0); }
    50% { opacity: 1; transform: scale(1); }
  }
  .anime-lines {
    position: absolute; inset: 0; overflow: hidden;
  }
  .speed-line {
    position: absolute; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,229,255,0.4), transparent);
    animation: speedLine 1.5s linear infinite;
  }
  @keyframes speedLine {
    0% { transform: translateX(-100%); opacity: 0; }
    50% { opacity: 1; }
    100% { transform: translateX(100%); opacity: 0; }
  }
  .play-overlay {
    position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
    background: rgba(0,0,0,0.3); opacity: 0; transition: opacity 0.2s;
    pointer-events: none;
  }
  .post-video:hover .play-overlay { opacity: 1; }
  .play-btn {
    width: 56px; height: 56px; border-radius: 50%;
    background: rgba(255,255,255,0.2); backdrop-filter: blur(10px);
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; border: 2px solid rgba(255,255,255,0.4);
  }
  .animated-badge {
    position: absolute; top: 12px; right: 12px;
    padding: 4px 10px; border-radius: 12px;
    background: rgba(0,0,0,0.6); backdrop-filter: blur(8px);
    font-size: 11px; font-weight: 700; color: var(--accent);
    border: 1px solid rgba(0,229,255,0.4);
    font-family: 'Orbitron', sans-serif;
  }

  /* POST ACTIONS */
  .post-actions { display: flex; align-items: center; gap: 16px; padding: 14px 16px; }
  .action-btn {
    display: flex; align-items: center; gap: 6px;
    background: none; border: none; cursor: pointer;
    color: var(--muted); font-size: 14px; font-family: 'Nunito', sans-serif;
    font-weight: 600; transition: color 0.2s; padding: 6px 10px; border-radius: 8px;
  }
  .action-btn:hover { color: var(--text); background: var(--surface2); }
  .action-btn.liked { color: var(--accent2); }
  .action-btn .icon { font-size: 18px; }
  .post-caption { padding: 0 16px 16px; font-size: 14px; color: var(--muted); line-height: 1.5; }
  .post-caption strong { color: var(--text); }
  .post-video-el { width: 100%; height: 100%; object-fit: cover; background: #000; }
  .feed-state {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 14px;
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 16px;
  }
  .feed-error {
    background: rgba(255,45,120,0.12);
    border: 1px solid rgba(255,45,120,0.35);
    border-radius: 12px;
    padding: 12px;
    color: #ff9ebb;
    font-size: 13px;
    margin-bottom: 16px;
  }
  .feed-notice {
    background: rgba(0,229,255,0.08);
    border: 1px solid rgba(0,229,255,0.25);
    border-radius: 12px;
    padding: 12px;
    color: var(--accent);
    font-size: 13px;
    margin-bottom: 16px;
  }
  .comments-panel {
    border-top: 1px solid var(--border);
    padding: 12px 16px 16px;
    background: rgba(20,26,40,0.5);
  }
  .comments-list {
    max-height: 180px;
    overflow-y: auto;
    margin-bottom: 10px;
  }
  .comment-item {
    padding: 8px 0;
    border-bottom: 1px solid rgba(30,45,69,0.5);
  }
  .comment-item:last-child { border-bottom: none; }
  .comment-author { font-size: 12px; font-weight: 700; color: var(--text); margin-bottom: 2px; }
  .comment-content { font-size: 13px; color: var(--muted); }
  .comment-input-row {
    display: flex;
    gap: 8px;
    align-items: center;
  }
  .comment-input {
    flex: 1;
    border: 1px solid var(--border);
    background: var(--surface2);
    color: var(--text);
    border-radius: 8px;
    padding: 8px 10px;
    font-size: 13px;
    font-family: 'Nunito', sans-serif;
  }
  .comment-input:focus {
    outline: none;
    border-color: rgba(0,229,255,0.45);
  }
  .comment-send {
    border: 1px solid rgba(0,229,255,0.3);
    background: rgba(0,229,255,0.08);
    color: var(--accent);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
  }
  .comment-send:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* FEED RIGHT */
  .feed-right { width: 300px; padding: 24px 20px; flex-shrink: 0; }
  .trending-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 14px; padding: 18px; margin-bottom: 16px;
  }
  .trending-title {
    font-family: 'Orbitron', sans-serif; font-size: 11px; font-weight: 700;
    color: var(--accent); letter-spacing: 2px; text-transform: uppercase; margin-bottom: 14px;
  }
  .trending-item { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid var(--border); }
  .trending-item:last-child { border-bottom: none; }
  .trending-num { font-family: 'Orbitron', sans-serif; font-size: 18px; font-weight: 900; color: var(--border); min-width: 28px; }
  .trending-info { flex: 1; }
  .trending-tag { font-size: 13px; font-weight: 700; }
  .trending-count { font-size: 11px; color: var(--muted); }
  .privacy-meter {
    background: var(--surface); border: 1px solid rgba(168,85,247,0.3);
    border-radius: 14px; padding: 18px; margin-bottom: 16px;
  }
  .privacy-title {
    font-family: 'Orbitron', sans-serif; font-size: 11px; font-weight: 700;
    color: var(--accent3); letter-spacing: 2px; margin-bottom: 14px;
  }
  .privacy-stat { margin-bottom: 10px; }
  .privacy-label { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px; }
  .privacy-bar { height: 6px; background: var(--surface2); border-radius: 3px; overflow: hidden; }
  .privacy-fill { height: 100%; border-radius: 3px; background: linear-gradient(90deg, var(--accent3), var(--accent)); transition: width 1s; }

  /* ========== UPLOAD ========== */
  .upload-page { max-width: 900px; margin: 0 auto; padding: 40px 24px; }
  .upload-title {
    font-family: 'Orbitron', sans-serif; font-size: 28px; font-weight: 900;
    background: linear-gradient(135deg, var(--accent), var(--accent3));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
  }
  .upload-subtitle { color: var(--muted); font-size: 15px; margin-bottom: 40px; }
  .upload-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; }

  .drop-zone {
    border: 2px dashed var(--border); border-radius: 20px;
    padding: 48px 24px; text-align: center; cursor: pointer;
    background: var(--surface); transition: all 0.3s;
    position: relative; overflow: hidden;
  }
  .drop-zone:hover, .drop-zone.dragover {
    border-color: var(--accent);
    background: rgba(0,229,255,0.05);
    box-shadow: var(--glow);
  }
  .drop-icon { font-size: 56px; margin-bottom: 16px; display: block; }
  .drop-title { font-size: 18px; font-weight: 700; margin-bottom: 8px; }
  .drop-sub { color: var(--muted); font-size: 14px; margin-bottom: 20px; }
  .drop-formats { display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; }
  .format-tag {
    padding: 4px 10px; border-radius: 8px;
    background: var(--surface2); border: 1px solid var(--border);
    font-size: 12px; color: var(--muted);
  }
  .hidden-input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }

  .process-panel { }
  .process-steps { margin-bottom: 24px; }
  .process-step {
    display: flex; align-items: center; gap: 14px;
    padding: 14px 16px; background: var(--surface); border-radius: 12px;
    margin-bottom: 8px; border: 1px solid var(--border);
    transition: all 0.3s;
  }
  .process-step.active { border-color: var(--accent); background: rgba(0,229,255,0.05); }
  .process-step.done { border-color: rgba(0,229,255,0.3); }
  .step-num {
    width: 32px; height: 32px; border-radius: 50%;
    background: var(--surface2); display: flex; align-items: center; justify-content: center;
    font-family: 'Orbitron', sans-serif; font-size: 13px; font-weight: 700;
    flex-shrink: 0; transition: all 0.3s;
  }
  .process-step.active .step-num { background: var(--accent); color: var(--bg); }
  .process-step.done .step-num { background: rgba(0,229,255,0.2); color: var(--accent); }
  .step-info { flex: 1; }
  .step-name { font-weight: 700; font-size: 14px; }
  .step-desc { font-size: 12px; color: var(--muted); margin-top: 2px; }
  .step-status { font-size: 18px; }

  .progress-bar-wrap { background: var(--surface); border-radius: 14px; padding: 18px; }
  .progress-title { font-size: 13px; font-weight: 700; margin-bottom: 10px; display: flex; justify-content: space-between; }
  .progress-track { height: 8px; background: var(--surface2); border-radius: 4px; overflow: hidden; margin-bottom: 12px; }
  .progress-fill {
    height: 100%; border-radius: 4px;
    background: linear-gradient(90deg, var(--accent3), var(--accent));
    transition: width 0.3s;
    box-shadow: 0 0 10px rgba(0,229,255,0.5);
  }
  .progress-detail { font-size: 12px; color: var(--muted); }

  .upload-btn {
    width: 100%; padding: 14px; border-radius: 12px;
    background: linear-gradient(135deg, var(--accent2), var(--accent3));
    border: none; color: white; font-family: 'Nunito', sans-serif;
    font-size: 16px; font-weight: 700; cursor: pointer;
    box-shadow: var(--glow2); margin-top: 16px;
    transition: transform 0.2s, opacity 0.2s;
  }
  .upload-btn:hover { transform: scale(1.02); }
  .upload-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
  .publish-panel {
    margin-top: 14px;
    padding: 14px;
    border-radius: 12px;
    background: var(--surface);
    border: 1px solid var(--border);
  }
  .publish-title {
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 8px;
  }
  .caption-input {
    width: 100%;
    min-height: 80px;
    resize: vertical;
    border: 1px solid var(--border);
    background: var(--surface2);
    color: var(--text);
    border-radius: 10px;
    padding: 10px;
    font-size: 13px;
    font-family: 'Nunito', sans-serif;
  }
  .caption-input:focus {
    outline: none;
    border-color: rgba(0,229,255,0.45);
  }
  .publish-meta {
    margin-top: 10px;
    font-size: 12px;
    color: var(--muted);
  }

  /* PREVIEW */
  .preview-section { margin-top: 28px; }
  .preview-title { font-size: 14px; font-weight: 700; margin-bottom: 14px; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; }
  .preview-compare { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .preview-box { border-radius: 12px; overflow: hidden; border: 1px solid var(--border); }
  .preview-label {
    padding: 8px 12px; font-size: 11px; font-weight: 700;
    letter-spacing: 1px; background: var(--surface);
  }
  .preview-label.original { color: var(--muted); }
  .preview-label.animated { color: var(--accent); }
  .preview-media { aspect-ratio: 9/16; max-height: 200px; background: var(--surface2); display: flex; align-items: center; justify-content: center; font-size: 40px; }
  .vs-divider { display: flex; align-items: center; justify-content: center; font-family: 'Orbitron', sans-serif; font-weight: 900; color: var(--accent2); font-size: 20px; }

  /* ========== ARCHITECTURE ========== */
  .arch-page { max-width: 1000px; margin: 0 auto; padding: 40px 24px; }
  .arch-title {
    font-family: 'Orbitron', sans-serif; font-size: 28px; font-weight: 900;
    background: linear-gradient(135deg, var(--accent2), var(--accent3));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
  }
  .arch-subtitle { color: var(--muted); font-size: 15px; margin-bottom: 40px; }
  .arch-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 32px; }
  .arch-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 16px; padding: 20px;
    transition: border-color 0.2s;
  }
  .arch-card:hover { border-color: rgba(0,229,255,0.3); }
  .arch-card-icon { font-size: 32px; margin-bottom: 12px; }
  .arch-card-title { font-family: 'Orbitron', sans-serif; font-size: 12px; font-weight: 700; color: var(--accent); letter-spacing: 1px; margin-bottom: 8px; }
  .arch-card-desc { font-size: 13px; color: var(--muted); line-height: 1.6; }
  .arch-card-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
  .tech-tag {
    padding: 3px 8px; border-radius: 6px;
    background: rgba(0,229,255,0.08); border: 1px solid rgba(0,229,255,0.2);
    font-size: 11px; color: var(--accent);
  }
  .tech-tag.pink { background: rgba(255,45,120,0.08); border-color: rgba(255,45,120,0.2); color: var(--accent2); }
  .tech-tag.purple { background: rgba(168,85,247,0.08); border-color: rgba(168,85,247,0.2); color: var(--accent3); }

  .flow-diagram { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 28px; margin-bottom: 32px; }
  .flow-title { font-family: 'Orbitron', sans-serif; font-size: 13px; color: var(--accent); letter-spacing: 2px; margin-bottom: 24px; text-transform: uppercase; }
  .flow-steps { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; }
  .flow-step {
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 10px; padding: 12px 16px; min-width: 120px;
  }
  .flow-step-icon { font-size: 20px; margin-bottom: 4px; }
  .flow-step-name { font-size: 12px; font-weight: 700; }
  .flow-step-detail { font-size: 11px; color: var(--muted); margin-top: 2px; }
  .flow-arrow { font-size: 20px; color: var(--accent); font-weight: 900; }

  .privacy-guarantees { background: var(--surface); border: 1px solid rgba(168,85,247,0.3); border-radius: 16px; padding: 28px; }
  .privacy-g-title { font-family: 'Orbitron', sans-serif; font-size: 13px; color: var(--accent3); letter-spacing: 2px; margin-bottom: 20px; text-transform: uppercase; }
  .guarantee-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .guarantee-item {
    display: flex; align-items: flex-start; gap: 10px;
    background: rgba(168,85,247,0.05); border-radius: 10px; padding: 14px;
  }
  .guarantee-icon { font-size: 20px; flex-shrink: 0; }
  .guarantee-text { font-size: 13px; line-height: 1.5; color: var(--muted); }
  .guarantee-text strong { color: var(--text); display: block; margin-bottom: 2px; font-size: 13px; }

  /* ========== ROADMAP ========== */
  .roadmap-page { max-width: 900px; margin: 0 auto; padding: 40px 24px; }
  .roadmap-title {
    font-family: 'Orbitron', sans-serif; font-size: 28px; font-weight: 900;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
  }
  .roadmap-subtitle { color: var(--muted); font-size: 15px; margin-bottom: 40px; }
  .roadmap-phases { position: relative; }
  .roadmap-phases::before {
    content: ''; position: absolute; left: 24px; top: 0; bottom: 0;
    width: 2px; background: linear-gradient(to bottom, var(--accent), var(--accent3), var(--accent2), var(--border));
  }
  .phase-item { display: flex; gap: 24px; margin-bottom: 28px; position: relative; }
  .phase-dot {
    width: 50px; height: 50px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Orbitron', sans-serif; font-size: 13px; font-weight: 900;
    flex-shrink: 0; z-index: 1;
    border: 2px solid var(--border);
  }
  .phase-dot.current { background: var(--accent); color: var(--bg); border-color: var(--accent); box-shadow: var(--glow); }
  .phase-dot.upcoming { background: var(--surface2); color: var(--muted); }
  .phase-dot.future { background: var(--surface); color: var(--border); }
  .phase-card {
    flex: 1; background: var(--surface); border: 1px solid var(--border);
    border-radius: 14px; padding: 20px; transition: border-color 0.2s;
  }
  .phase-card:hover { border-color: rgba(0,229,255,0.3); }
  .phase-header { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
  .phase-name { font-family: 'Orbitron', sans-serif; font-size: 14px; font-weight: 700; }
  .phase-timeline {
    margin-left: auto; padding: 4px 10px; border-radius: 10px;
    background: var(--surface2); font-size: 12px; font-weight: 700; color: var(--muted);
    font-family: 'Orbitron', sans-serif;
  }
  .phase-desc { font-size: 14px; color: var(--muted); margin-bottom: 14px; line-height: 1.5; }
  .phase-features { display: flex; flex-wrap: wrap; gap: 8px; }
  .feature-chip {
    padding: 5px 12px; border-radius: 10px; font-size: 12px; font-weight: 600;
    background: var(--surface2); border: 1px solid var(--border); color: var(--muted);
  }
  .feature-chip.done { color: var(--accent); border-color: rgba(0,229,255,0.3); background: rgba(0,229,255,0.07); }
  .feature-chip.inprogress { color: #fbbf24; border-color: rgba(251,191,36,0.3); background: rgba(251,191,36,0.07); }

  .roadmap-metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 32px; }
  .metric-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 14px; padding: 18px; text-align: center;
  }
  .metric-num { font-family: 'Orbitron', sans-serif; font-size: 28px; font-weight: 900; }
  .metric-num.cyan { color: var(--accent); }
  .metric-num.pink { color: var(--accent2); }
  .metric-num.purple { color: var(--accent3); }
  .metric-num.gold { color: #fbbf24; }
  .metric-label { font-size: 11px; color: var(--muted); margin-top: 4px; text-transform: uppercase; letter-spacing: 1px; }
`;

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/+$/, "");
const ACCESS_TOKEN_KEY = "animface_access_token";
const SAVED_POSTS_KEY = "animface_saved_posts";

const toApiUrl = (path) => `${API_BASE_URL}${path}`;
const toPublicUrl = (path) => {
  if (!path) return "";
  const normalized = String(path).replace(/\\/g, "/");
  if (normalized.startsWith("http://") || normalized.startsWith("https://")) return normalized;
  return `${API_BASE_URL}${normalized.startsWith("/") ? normalized : `/${normalized}`}`;
};

const getStoredToken = () => localStorage.getItem(ACCESS_TOKEN_KEY);
const setStoredToken = (token) => localStorage.setItem(ACCESS_TOKEN_KEY, token);
const clearStoredToken = () => localStorage.removeItem(ACCESS_TOKEN_KEY);

const safeJson = async (response) => {
  try {
    return await response.json();
  } catch {
    return null;
  }
};

const formatApiError = (detail, fallback) => {
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const first = detail[0];
    if (typeof first === "string") return first;
    if (first && typeof first === "object") {
      return first.msg || first.message || fallback;
    }
  }
  if (typeof detail === "object") {
    return detail.message || detail.msg || fallback;
  }
  return fallback;
};

const createGuestIdentity = () => {
  const suffix = Math.random().toString(36).slice(2, 10);
  return {
    username: `guest_${suffix}`,
    email: `guest_${suffix}@example.com`,
    password: `GuestPass_${suffix}_A1`,
    avatar_emoji: "USER",
  };
};

const loadSavedPosts = () => {
  try {
    const raw = localStorage.getItem(SAVED_POSTS_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((item) => item && typeof item.id === "string");
  } catch {
    return [];
  }
};

const persistSavedPosts = (posts) => {
  localStorage.setItem(SAVED_POSTS_KEY, JSON.stringify(posts));
};

const styleLabel = (style) => {
  const lookup = {
    anime: "Anime",
    sketch: "Sketch",
    soft: "Soft",
    action: "Action",
  };
  return lookup[String(style || "").toLowerCase()] || "Anime";
};

const styleColor = (style) => {
  const lookup = {
    anime: "#00e5ff",
    sketch: "#8bd3ff",
    soft: "#a855f7",
    action: "#ff2d78",
  };
  return lookup[String(style || "").toLowerCase()] || "#00e5ff";
};

const initialsFromUsername = (username) => {
  const source = String(username || "").replace(/[^a-zA-Z0-9]/g, "");
  if (!source) return "US";
  return source.slice(0, 2).toUpperCase();
};

const toRelativeTime = (value) => {
  if (!value) return "now";
  const ts = new Date(value).getTime();
  if (Number.isNaN(ts)) return "now";
  const deltaSeconds = Math.max(1, Math.floor((Date.now() - ts) / 1000));
  if (deltaSeconds < 60) return `${deltaSeconds}s ago`;
  if (deltaSeconds < 3600) return `${Math.floor(deltaSeconds / 60)}m ago`;
  if (deltaSeconds < 86400) return `${Math.floor(deltaSeconds / 3600)}h ago`;
  return `${Math.floor(deltaSeconds / 86400)}d ago`;
};

const ensureAccessToken = async () => {
  const token = getStoredToken();
  if (token) return token;

  const payload = createGuestIdentity();
  const response = await fetch(toApiUrl("/api/v1/auth/register"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await safeJson(response);
  if (!response.ok || !data?.access_token) {
    const detail = formatApiError(data?.detail, `Auth failed (${response.status})`);
    throw new Error(detail);
  }

  setStoredToken(data.access_token);
  return data.access_token;
};

const fetchWithAuth = async (path, options = {}) => {
  let token = await ensureAccessToken();

  const doRequest = async (activeToken) => {
    const headers = { ...(options.headers || {}), Authorization: `Bearer ${activeToken}` };
    return fetch(toApiUrl(path), { ...options, headers });
  };

  let response = await doRequest(token);
  if (response.status === 401) {
    clearStoredToken();
    token = await ensureAccessToken();
    response = await doRequest(token);
  }

  const data = await safeJson(response);
  if (!response.ok) {
    const method = (options.method || "GET").toUpperCase();
    const detail = formatApiError(data?.detail, `${method} ${path} failed (${response.status})`);
    throw new Error(detail);
  }

  return data;
};

const normalizePost = (post) => {
  const username = post?.author?.username || "user";
  const style = String(post?.video?.anime_style || "anime").toLowerCase();
  return {
    id: String(post?.id),
    user: username,
    emoji: initialsFromUsername(post?.author?.avatar_emoji || username),
    likes: Number(post?.like_count || 0),
    comments: Number(post?.comment_count || 0),
    caption: String(post?.caption || ""),
    time: toRelativeTime(post?.created_at),
    char: styleLabel(style).slice(0, 2).toUpperCase(),
    charColor: styleColor(style),
    style,
    videoUrl: toPublicUrl(post?.video?.animated_path),
    isLiked: Boolean(post?.is_liked),
  };
};

const AnimeScene = ({ char, colorHint }) => {
  const colors = { "#00e5ff": ["#001a2e", "#0a0030"], "#ff2d78": ["#2a0010", "#180020"], "#a855f7": ["#1a0028", "#0a0020"] };
  const [c1, c2] = colors[colorHint] || colors["#00e5ff"];
  return (
    <div className="anime-canvas">
      <div className="anime-bg" style={{ background: `linear-gradient(160deg, #080b14 0%, ${c1} 50%, ${c2} 100%)` }} />
      <div className="anime-lines">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="speed-line" style={{ top: `${20 + i * 15}%`, width: `${60 + i * 8}%`, left: `${i * 5}%`, animationDelay: `${i * 0.3}s`, animationDuration: `${1.2 + i * 0.2}s` }} />
        ))}
      </div>
      <div className="anime-scene">
        <span className="anime-char">{char}</span>
        <div style={{ fontFamily: "'Orbitron'", fontSize: 10, color: colorHint, letterSpacing: 3, marginTop: 8, opacity: 0.8 }}>ANIMATED</div>
      </div>
      <div className="anime-sparkles">
        {["*", "+", "*", ".", "*"].map((s, i) => (
          <span key={i} className="sparkle" style={{
            top: `${10 + i * 18}%`, left: `${8 + i * 20}%`,
            animationDelay: `${i * 0.6}s`, color: colorHint
          }}>{s}</span>
        ))}
      </div>
    </div>
  );
};

const FeedPage = ({ refreshKey = 0 }) => {
  const [posts, setPosts] = useState([]);
  const [savedPosts, setSavedPosts] = useState(() => loadSavedPosts());
  const [likedPosts, setLikedPosts] = useState({});
  const [activeItem, setActiveItem] = useState("home");
  const [styleFilter, setStyleFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [errorText, setErrorText] = useState("");
  const [noticeText, setNoticeText] = useState("");
  const [openCommentsFor, setOpenCommentsFor] = useState("");
  const [commentsByPost, setCommentsByPost] = useState({});
  const [commentDraftByPost, setCommentDraftByPost] = useState({});
  const [commentsLoadingFor, setCommentsLoadingFor] = useState("");
  const [submittingCommentFor, setSubmittingCommentFor] = useState("");

  useEffect(() => {
    if (!noticeText) return undefined;
    const timer = window.setTimeout(() => setNoticeText(""), 2200);
    return () => window.clearTimeout(timer);
  }, [noticeText]);

  useEffect(() => {
    let cancelled = false;

    const loadFeed = async () => {
      if (activeItem !== "home" && activeItem !== "trending") {
        setLoading(false);
        setErrorText("");
        return;
      }

      setLoading(true);
      setErrorText("");
      try {
        const endpoint = activeItem === "trending" ? "/api/v1/feed/explore" : "/api/v1/feed/";
        const data = await fetchWithAuth(endpoint);
        if (cancelled) return;

        const nextPosts = Array.isArray(data?.posts) ? data.posts.map(normalizePost) : [];
        setPosts(nextPosts);

        const nextLikedMap = {};
        nextPosts.forEach((post) => {
          nextLikedMap[post.id] = Boolean(post.isLiked);
        });
        setLikedPosts(nextLikedMap);
      } catch (err) {
        if (cancelled) return;
        setPosts([]);
        setErrorText(err instanceof Error ? err.message : "Could not load feed.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    loadFeed();
    return () => {
      cancelled = true;
    };
  }, [activeItem, refreshKey]);

  const updatePostCollections = (postId, updater) => {
    setPosts((prev) => prev.map((post) => (post.id === postId ? updater(post) : post)));
    setSavedPosts((prev) => {
      const next = prev.map((post) => (post.id === postId ? updater(post) : post));
      persistSavedPosts(next);
      return next;
    });
  };

  const toggleLike = async (postId) => {
    const wasLiked = Boolean(likedPosts[postId]);
    const delta = wasLiked ? -1 : 1;

    setLikedPosts((prev) => ({ ...prev, [postId]: !wasLiked }));
    updatePostCollections(postId, (post) => ({
      ...post,
      isLiked: !wasLiked,
      likes: Math.max(0, post.likes + delta),
    }));

    try {
      const payload = await fetchWithAuth(`/api/v1/posts/${postId}/like`, { method: "POST" });
      const finalLiked = Boolean(payload?.liked);
      const finalCount = Number(payload?.like_count || 0);
      setLikedPosts((prev) => ({ ...prev, [postId]: finalLiked }));
      updatePostCollections(postId, (post) => ({
        ...post,
        isLiked: finalLiked,
        likes: Math.max(0, finalCount),
      }));
    } catch (err) {
      setLikedPosts((prev) => ({ ...prev, [postId]: wasLiked }));
      updatePostCollections(postId, (post) => ({
        ...post,
        isLiked: wasLiked,
        likes: Math.max(0, post.likes - delta),
      }));
      setErrorText(err instanceof Error ? err.message : "Could not update like.");
    }
  };

  const toggleSave = (post) => {
    setSavedPosts((prev) => {
      const exists = prev.some((item) => item.id === post.id);
      const next = exists ? prev.filter((item) => item.id !== post.id) : [post, ...prev];
      persistSavedPosts(next);
      setNoticeText(exists ? "Removed from saved posts." : "Saved for later.");
      return next;
    });
  };

  const sharePost = async (postId) => {
    const shareLink = `${window.location.origin}/post/${postId}`;
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(shareLink);
        setNoticeText("Post link copied.");
      } else {
        setNoticeText(`Link: ${shareLink}`);
      }
    } catch {
      setNoticeText(`Link: ${shareLink}`);
    }
  };

  const toggleComments = async (postId) => {
    if (openCommentsFor === postId) {
      setOpenCommentsFor("");
      return;
    }

    setOpenCommentsFor(postId);
    if (Array.isArray(commentsByPost[postId])) return;

    setCommentsLoadingFor(postId);
    try {
      const comments = await fetchWithAuth(`/api/v1/posts/${postId}/comments`);
      setCommentsByPost((prev) => ({
        ...prev,
        [postId]: Array.isArray(comments) ? comments : [],
      }));
    } catch (err) {
      setErrorText(err instanceof Error ? err.message : "Could not load comments.");
    } finally {
      setCommentsLoadingFor("");
    }
  };

  const submitComment = async (postId) => {
    const draft = String(commentDraftByPost[postId] || "").trim();
    if (!draft || submittingCommentFor === postId) return;

    setSubmittingCommentFor(postId);
    try {
      const comment = await fetchWithAuth(`/api/v1/posts/${postId}/comments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: draft }),
      });
      setCommentsByPost((prev) => ({
        ...prev,
        [postId]: [comment, ...(prev[postId] || [])],
      }));
      setCommentDraftByPost((prev) => ({ ...prev, [postId]: "" }));
      updatePostCollections(postId, (post) => ({ ...post, comments: post.comments + 1 }));
    } catch (err) {
      setErrorText(err instanceof Error ? err.message : "Could not post comment.");
    } finally {
      setSubmittingCommentFor("");
    }
  };

  const basePosts = activeItem === "saved" ? savedPosts : posts;
  const filteredPosts = basePosts.filter((post) => styleFilter === "all" || post.style === styleFilter);
  const stories = [
    { name: "You", emoji: "+", isAdd: true },
    ...posts
      .slice(0, 6)
      .map((post) => ({ name: post.user, emoji: initialsFromUsername(post.user), isAdd: false })),
  ];
  const emptyMessage = activeItem === "saved"
    ? "No saved posts yet."
    : activeItem === "notif"
      ? "Notifications are not available yet."
      : activeItem === "home"
        ? "No posts in your home feed yet. Upload and publish a video to get started."
        : "No posts found in explore.";

  return (
    <div className="feed-page">
      <aside className="feed-sidebar">
        <div className="sidebar-section">
          <div className="sidebar-title">Menu</div>
          {[["H", "Home", "home"], ["T", "Trending", "trending"], ["S", "Saved", "saved"], ["N", "Notifications", "notif"]].map(([icon, label, key]) => (
            <div key={key} className={`sidebar-item ${activeItem === key ? "active" : ""}`} onClick={() => setActiveItem(key)}>
              <span className="sidebar-icon">{icon}</span>{label}
            </div>
          ))}
        </div>
        <div className="sidebar-section">
          <div className="sidebar-title">Filter Style</div>
          {[["ALL", "All", "all"], ["AN", "Anime", "anime"], ["SK", "Sketch", "sketch"], ["SF", "Soft", "soft"], ["AC", "Action", "action"]].map(([icon, label, key]) => (
            <div key={label} className={`sidebar-item ${styleFilter === key ? "active" : ""}`} onClick={() => setStyleFilter(key)}>
              <span className="sidebar-icon">{icon}</span>{label}
            </div>
          ))}
        </div>
      </aside>

      <main className="feed-main">
        <div className="feed-header">
          <span className="feed-title">// LIVE FEED</span>
          <span style={{ fontSize: 12, color: "var(--muted)" }}>All faces anonymized</span>
        </div>

        {noticeText ? <div className="feed-notice">{noticeText}</div> : null}
        {errorText ? <div className="feed-error">{errorText}</div> : null}

        <div className="story-bar">
          {stories.map((s, i) => (
            <div key={i} className={`story-item ${s.isAdd ? "story-add" : ""}`}>
              <div className="story-ring">
                <div className="story-avatar">{s.emoji}</div>
              </div>
              <span className="story-name">{s.name}</span>
            </div>
          ))}
        </div>

        {loading ? <div className="feed-state">Loading posts...</div> : null}

        {!loading && filteredPosts.length === 0 ? <div className="feed-state">{emptyMessage}</div> : null}

        {filteredPosts.map((post) => {
          const comments = commentsByPost[post.id] || [];
          const isSaved = savedPosts.some((item) => item.id === post.id);
          const isLikeOn = Boolean(likedPosts[post.id]);
          return (
          <div key={post.id} className="post-card">
            <div className="post-header">
              <div className="post-avatar-wrap">
                <div className="post-avatar">{post.emoji}</div>
              </div>
              <div>
                <div className="post-user-name">@{post.user}</div>
                <div className="post-time">{post.time}</div>
              </div>
              <div className="post-privacy-badge">Anonymous</div>
            </div>
            <div className="post-video">
              {post.videoUrl ? (
                <video className="post-video-el" src={post.videoUrl} controls preload="metadata" />
              ) : (
                <AnimeScene char={post.char} colorHint={post.charColor} />
              )}
              <div className="animated-badge">{styleLabel(post.style).toUpperCase()}</div>
              {!post.videoUrl ? <div className="play-overlay"><div className="play-btn">{">"}</div></div> : null}
            </div>
            <div className="post-actions">
              <button className={`action-btn ${isLikeOn ? "liked" : ""}`} onClick={() => toggleLike(post.id)}>
                <span className="icon">{isLikeOn ? "ON" : "LIKE"}</span>
                {post.likes}
              </button>
              <button className="action-btn" onClick={() => toggleComments(post.id)}><span className="icon">COM</span>{post.comments}</button>
              <button className="action-btn" onClick={() => sharePost(post.id)}><span className="icon">SHR</span>Share</button>
              <button className={`action-btn ${isSaved ? "liked" : ""}`} style={{ marginLeft: "auto" }} onClick={() => toggleSave(post)}>
                {isSaved ? "SAVED" : "SAVE"}
              </button>
            </div>
            <div className="post-caption"><strong>@{post.user}</strong> {post.caption}</div>

            {openCommentsFor === post.id ? (
              <div className="comments-panel">
                {commentsLoadingFor === post.id ? <div className="feed-state" style={{ marginBottom: 8 }}>Loading comments...</div> : null}
                <div className="comments-list">
                  {commentsLoadingFor !== post.id && comments.length === 0 ? (
                    <div className="comment-content">No comments yet.</div>
                  ) : null}
                  {comments.map((comment) => (
                    <div key={String(comment.id)} className="comment-item">
                      <div className="comment-author">@{comment?.author?.username || "user"}</div>
                      <div className="comment-content">{comment?.content || ""}</div>
                    </div>
                  ))}
                </div>
                <div className="comment-input-row">
                  <input
                    className="comment-input"
                    placeholder="Add a comment..."
                    value={commentDraftByPost[post.id] || ""}
                    onChange={(event) => setCommentDraftByPost((prev) => ({ ...prev, [post.id]: event.target.value }))}
                    onKeyDown={(event) => {
                      if (event.key === "Enter") {
                        event.preventDefault();
                        submitComment(post.id);
                      }
                    }}
                  />
                  <button className="comment-send" onClick={() => submitComment(post.id)} disabled={submittingCommentFor === post.id}>
                    {submittingCommentFor === post.id ? "..." : "Post"}
                  </button>
                </div>
              </div>
            ) : null}
          </div>
        );
        })}
      </main>

      <aside className="feed-right">
        <div className="privacy-meter">
          <div className="privacy-title">PRIVACY STATS</div>
          {[["Faces Hidden", 100], ["Location Masked", 100], ["Voice Altered", 87], ["Metadata Stripped", 100]].map(([label, val]) => (
            <div key={label} className="privacy-stat">
              <div className="privacy-label"><span>{label}</span><span style={{ color: "var(--accent)" }}>{val}%</span></div>
              <div className="privacy-bar"><div className="privacy-fill" style={{ width: `${val}%` }} /></div>
            </div>
          ))}
        </div>
        <div className="trending-card">
          <div className="trending-title">Trending</div>
          {[["#animelife", "24.2K"], ["#faceless", "18.9K"], ["#ghostmode", "15.3K"], ["#animevibe", "12.1K"]].map(([tag, count], i) => (
            <div key={tag} className="trending-item">
              <span className="trending-num" style={{ color: i === 0 ? "var(--accent2)" : undefined }}>0{i + 1}</span>
              <div className="trending-info">
                <div className="trending-tag">{tag}</div>
                <div className="trending-count">{count} videos</div>
              </div>
            </div>
          ))}
        </div>
      </aside>
    </div>
  );
};

const UploadPage = ({ onPublished }) => {
  const [progress, setProgress] = useState(0);
  const [step, setStep] = useState(0);
  const [dragging, setDragging] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [done, setDone] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [originalPreviewUrl, setOriginalPreviewUrl] = useState("");
  const [animatedUrl, setAnimatedUrl] = useState("");
  const [videoId, setVideoId] = useState("");
  const [statusText, setStatusText] = useState("Select a video and start conversion.");
  const [errorText, setErrorText] = useState("");
  const [animeStyle, setAnimeStyle] = useState("anime");
  const [captionText, setCaptionText] = useState("");
  const [publishing, setPublishing] = useState(false);
  const [publishText, setPublishText] = useState("");
  const [publishedPostId, setPublishedPostId] = useState("");
  const pollRef = useRef(null);

  const steps = [
    { name: "Upload Video", desc: "Send video to backend", icon: "UP" },
    { name: "Face Detection", desc: "AI scans initial frames", icon: "FD" },
    { name: "Animation Conversion", desc: "Backend applies anime style", icon: "AN" },
    { name: "Privacy Strip", desc: "Metadata cleanup", icon: "PR" },
    { name: "Ready to Share", desc: "Converted output available", icon: "OK" },
  ];

  const statusToStep = (status) => {
    const map = {
      uploading: 0,
      uploaded: 0,
      processing: 1,
      face_detection: 1,
      animating: 2,
      privacy_strip: 3,
      ready: 4,
      failed: 3,
    };
    return map[status] ?? 0;
  };

  const stopPolling = () => {
    if (pollRef.current) {
      window.clearInterval(pollRef.current);
      pollRef.current = null;
    }
  };

  useEffect(() => () => stopPolling(), []);

  useEffect(() => () => {
    if (originalPreviewUrl && originalPreviewUrl.startsWith("blob:")) {
      URL.revokeObjectURL(originalPreviewUrl);
    }
  }, [originalPreviewUrl]);

  const applyStatusUpdate = (payload) => {
    const nextStatus = payload?.status || "processing";
    const nextProgress = typeof payload?.processing_progress === "number" ? payload.processing_progress : 0;

    setProgress(Math.max(0, Math.min(100, nextProgress)));
    setStep(statusToStep(nextStatus));

    if (nextStatus === "ready") {
      setDone(true);
      setProcessing(false);
      setProgress(100);
      setStep(4);
      setAnimatedUrl(toPublicUrl(payload.animated_path));
      setStatusText("Animation complete. Converted video is ready.");
      return;
    }

    if (nextStatus === "failed") {
      setDone(false);
      setProcessing(false);
      setErrorText(payload?.error_message || "Video conversion failed.");
      setStatusText("Conversion failed.");
      return;
    }

    setDone(false);
    setProcessing(true);
    setStatusText(`Processing: ${String(nextStatus).replace(/_/g, " ")}`);
  };

  const fetchAndApplyStatus = async (id, token) => {
    let activeToken = token;
    let response = await fetch(toApiUrl(`/api/v1/videos/${id}/status`), {
      headers: { Authorization: `Bearer ${activeToken}` },
    });

    if (response.status === 401) {
      clearStoredToken();
      activeToken = await ensureAccessToken();
      response = await fetch(toApiUrl(`/api/v1/videos/${id}/status`), {
        headers: { Authorization: `Bearer ${activeToken}` },
      });
    }

    const data = await safeJson(response);
    if (!response.ok || !data) {
      const detail = formatApiError(data?.detail, `Status check failed (${response.status})`);
      throw new Error(detail);
    }

    applyStatusUpdate(data);
    return { status: data.status, token: activeToken };
  };

  const handlePickedFile = (file) => {
    if (!file) return;

    if (!String(file.type || "").startsWith("video/")) {
      setErrorText("Please select a valid video file.");
      return;
    }

    stopPolling();
    setDone(false);
    setProcessing(false);
    setProgress(0);
    setStep(0);
    setAnimatedUrl("");
    setVideoId("");
    setErrorText("");
    setCaptionText("");
    setPublishText("");
    setPublishedPostId("");
    setSelectedFile(file);
    setStatusText(`Selected: ${file.name}`);

    setOriginalPreviewUrl((prev) => {
      if (prev && prev.startsWith("blob:")) URL.revokeObjectURL(prev);
      return URL.createObjectURL(file);
    });
  };

  const handleInputChange = (event) => {
    const file = event.target.files?.[0];
    handlePickedFile(file);
    event.target.value = "";
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragging(false);
    const file = event.dataTransfer.files?.[0];
    handlePickedFile(file);
  };

  const startConversion = async () => {
    if (processing) return;
    if (!selectedFile) {
      setErrorText("Pick a video file first.");
      return;
    }

    stopPolling();
    setProcessing(true);
    setDone(false);
    setProgress(0);
    setStep(0);
    setVideoId("");
    setAnimatedUrl("");
    setErrorText("");
    setPublishText("");
    setPublishedPostId("");
    setStatusText("Authenticating...");

    try {
      let token = await ensureAccessToken();
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("anime_style", animeStyle);

      const upload = async (authToken) => fetch(toApiUrl("/api/v1/videos/upload"), {
        method: "POST",
        headers: { Authorization: `Bearer ${authToken}` },
        body: formData,
      });

      setStatusText("Uploading video...");
      let uploadResponse = await upload(token);

      if (uploadResponse.status === 401) {
        clearStoredToken();
        token = await ensureAccessToken();
        uploadResponse = await upload(token);
      }

      const uploadData = await safeJson(uploadResponse);
      if (!uploadResponse.ok || !uploadData?.id) {
        const detail = formatApiError(uploadData?.detail, `Upload failed (${uploadResponse.status})`);
        throw new Error(detail);
      }

      setVideoId(uploadData.id);
      setStatusText("Upload successful. Starting conversion...");
      setStep(1);

      const pollOnce = async () => {
        const result = await fetchAndApplyStatus(uploadData.id, token);
        token = result.token;
        if (result.status === "ready" || result.status === "failed") {
          stopPolling();
        }
        return result.status;
      };

      const firstStatus = await pollOnce();
      if (firstStatus !== "ready" && firstStatus !== "failed") {
        pollRef.current = window.setInterval(() => {
          pollOnce().catch((err) => {
            stopPolling();
            setProcessing(false);
            setErrorText(err instanceof Error ? err.message : "Status polling failed.");
            setStatusText("Conversion interrupted.");
          });
        }, 2000);
      }
    } catch (err) {
      stopPolling();
      setProcessing(false);
      setDone(false);
      setErrorText(err instanceof Error ? err.message : "Could not start conversion.");
      setStatusText("Conversion could not start.");
    }
  };

  const publishPost = async () => {
    if (!videoId || !done || publishing) return;

    setPublishing(true);
    setPublishText("");
    try {
      const payload = await fetchWithAuth("/api/v1/posts/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          video_id: videoId,
          caption: captionText.trim() || null,
          is_public: true,
          comments_enabled: true,
        }),
      });

      setPublishedPostId(String(payload?.id || ""));
      setPublishText("Post published successfully.");
      if (typeof onPublished === "function") {
        onPublished();
      }
    } catch (err) {
      if (err instanceof TypeError) {
        setPublishText("Could not reach API while publishing. Confirm backend is running on port 8000.");
      } else {
        setPublishText(err instanceof Error ? err.message : "Could not publish post.");
      }
    } finally {
      setPublishing(false);
    }
  };

  return (
    <div className="upload-page">
      <div className="upload-title">UPLOAD & ANIMATE</div>
      <div className="upload-subtitle">Your video is converted on the backend and tracked in real time.</div>
      <div className="upload-layout">
        <div>
          <div className={`drop-zone ${dragging ? "dragover" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
          >
            <input type="file" className="hidden-input" accept="video/*" onChange={handleInputChange} />
            <span className="drop-icon">{done ? "OK" : processing ? "..." : "VID"}</span>
            <div className="drop-title">
              {done ? "Animation Complete" : processing ? "Processing" : selectedFile ? selectedFile.name : "Drop your video here"}
            </div>
            <div className="drop-sub">{done ? "Converted file ready" : "or click to browse - max 60 seconds"}</div>
            <div className="drop-formats">
              {["MP4", "MOV", "AVI", "WEBM"].map(f => <span key={f} className="format-tag">{f}</span>)}
            </div>
          </div>

          {(selectedFile || processing || done) && (
            <div className="preview-section">
              <div className="preview-title">Before & After</div>
              <div className="preview-compare">
                <div className="preview-box">
                  <div className="preview-label original">ORIGINAL</div>
                  <div className="preview-media" style={{ overflow: "hidden" }}>
                    {originalPreviewUrl ? (
                      <video
                        src={originalPreviewUrl}
                        controls
                        muted
                        style={{ width: "100%", height: "100%", objectFit: "cover" }}
                      />
                    ) : "-"}
                  </div>
                </div>
                <div className="vs-divider">{"->"}</div>
                <div className="preview-box">
                  <div className="preview-label animated">ANIMATED</div>
                  <div className="preview-media" style={{ background: "linear-gradient(135deg, #0a0015, #001a2e)", fontSize: 20, position: "relative", overflow: "hidden" }}>
                    {animatedUrl ? (
                      <video
                        src={animatedUrl}
                        controls
                        style={{ width: "100%", height: "100%", objectFit: "cover" }}
                      />
                    ) : (
                      <span>Waiting...</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="process-panel">
          <div style={{ display: "flex", gap: 8, marginBottom: 12, flexWrap: "wrap" }}>
            {["anime", "sketch", "soft", "action"].map((styleKey) => (
              <button
                key={styleKey}
                className="nav-tab"
                style={{ border: animeStyle === styleKey ? "1px solid rgba(0,229,255,0.3)" : "1px solid var(--border)" }}
                onClick={() => setAnimeStyle(styleKey)}
                disabled={processing}
              >
                {styleKey}
              </button>
            ))}
          </div>

          <div className="process-steps">
            {steps.map((s, i) => (
              <div key={i} className={`process-step ${step === i && processing ? "active" : step > i || done ? "done" : ""}`}>
                <div className="step-num">{step > i || done ? "OK" : i + 1}</div>
                <div className="step-info">
                  <div className="step-name">{s.name}</div>
                  <div className="step-desc">{s.desc}</div>
                </div>
                <span className="step-status">{step > i || done ? "OK" : step === i && processing ? ".." : s.icon}</span>
              </div>
            ))}
          </div>

          {(processing || done || progress > 0) ? (
            <div className="progress-bar-wrap">
              <div className="progress-title"><span>Progress</span><span style={{ color: "var(--accent)" }}>{progress}%</span></div>
              <div className="progress-track"><div className="progress-fill" style={{ width: `${progress}%` }} /></div>
              <div className="progress-detail">{errorText || statusText}</div>
            </div>
          ) : null}

          {errorText ? (
            <div style={{ marginTop: 12, color: "#ff6b8f", fontSize: 13, fontWeight: 700 }}>
              {errorText}
            </div>
          ) : null}

          {videoId ? (
            <div style={{ marginTop: 12, color: "var(--muted)", fontSize: 12 }}>
              Video ID: {videoId}
            </div>
          ) : null}

          <button className="upload-btn" onClick={startConversion} disabled={processing || !selectedFile}>
            {processing ? "Converting..." : "Start Animation"}
          </button>

          {done && animatedUrl ? (
            <button
              className="upload-btn"
              style={{ marginTop: 10, background: "linear-gradient(135deg, var(--accent), #00b8d4)" }}
              onClick={() => window.open(animatedUrl, "_blank", "noopener,noreferrer")}
            >
              Open Animated Video
            </button>
          ) : null}

          {done && videoId ? (
            <div className="publish-panel">
              <div className="publish-title">Publish to Feed</div>
              <textarea
                className="caption-input"
                value={captionText}
                onChange={(event) => setCaptionText(event.target.value)}
                placeholder="Write a caption (optional)"
                maxLength={500}
              />
              <button className="upload-btn" style={{ marginTop: 12 }} onClick={publishPost} disabled={publishing}>
                {publishing ? "Publishing..." : "Publish Post"}
              </button>
              {publishText ? <div className="publish-meta">{publishText}</div> : null}
              {publishedPostId ? <div className="publish-meta">Post ID: {publishedPostId}</div> : null}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};

const ArchPage = () => (
  <div className="arch-page">
    <div className="arch-title">TECH ARCHITECTURE</div>
    <div className="arch-subtitle">How AnimeFace is built - privacy-first from the ground up.</div>

    <div className="arch-grid">
      {[
        { icon: "FE", title: "FRONTEND", desc: "React SPA with PWA support. Client-side face detection using TensorFlow.js before upload - no raw face data ever leaves the device.", tags: ["React", "TailwindCSS", "PWA", "TensorFlow.js"], color: "cyan" },
        { icon: "API", title: "API LAYER", desc: "Node.js / FastAPI microservices. Stateless, horizontally scalable. JWT auth with short-lived tokens. Zero logging of PII.", tags: ["FastAPI", "Node.js", "Redis", "JWT"], color: "pink" },
        { icon: "AI", title: "AI PIPELINE", desc: "Custom anime GAN model fine-tuned on AnimeSR + CartoonGAN. Runs on GPU cluster. Input: anonymized frames. Output: anime frames.", tags: ["PyTorch", "CartoonGAN", "AnimeSR", "CUDA"], color: "purple" },
        { icon: "DB", title: "STORAGE", desc: "Processed videos stored encrypted (AES-256) in S3-compatible storage. No original video ever persisted. Only animated output saved.", tags: ["AWS S3", "AES-256", "Cloudflare R2"], color: "cyan" },
        { icon: "CDN", title: "CDN / DELIVERY", desc: "Animated videos served via Cloudflare CDN. Adaptive streaming (HLS). Videos expire from CDN after 30 days unless reshared.", tags: ["Cloudflare", "HLS", "WebRTC"], color: "pink" },
        { icon: "SEC", title: "PRIVACY LAYER", desc: "On-device face blurring before upload. Server-side metadata stripping. Voice morphing. Zero real-face storage policy enforced by design.", tags: ["On-device AI", "Metadata strip", "Voice morph"], color: "purple" },
      ].map(({ icon, title, desc, tags, color }) => (
        <div key={title} className="arch-card">
          <div className="arch-card-icon">{icon}</div>
          <div className="arch-card-title">{title}</div>
          <div className="arch-card-desc">{desc}</div>
          <div className="arch-card-tags">
            {tags.map(t => <span key={t} className={`tech-tag ${color}`}>{t}</span>)}
          </div>
        </div>
      ))}
    </div>

    <div className="flow-diagram">
      <div className="flow-title">Video Processing Flow</div>
      <div className="flow-steps">
        {[
          { icon: "REC", name: "User Records", detail: "Local device" },
          { icon: "AI", name: "On-Device AI", detail: "Face detect" },
          { icon: "ENC", name: "Encrypt & Upload", detail: "AES-256" },
          { icon: "GAN", name: "Anime GAN", detail: "GPU pipeline" },
          { icon: "DEL", name: "Delete Original", detail: "Zero trace" },
          { icon: "CDN", name: "CDN Publish", detail: "Anime only" },
        ].map((step, i, arr) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div className="flow-step">
              <div className="flow-step-icon">{step.icon}</div>
              <div className="flow-step-name">{step.name}</div>
              <div className="flow-step-detail">{step.detail}</div>
            </div>
            {i < arr.length - 1 && <div className="flow-arrow">{"->"}</div>}
          </div>
        ))}
      </div>
    </div>

    <div className="privacy-guarantees">
      <div className="privacy-g-title">Privacy Guarantees</div>
      <div className="guarantee-grid">
        {[
          ["NO", "No Face Storage", "Original facial data is never stored on any server. Detection runs fully on-device."],
          ["ID", "Zero Identity Link", "Anime avatar is algorithmically distinct - no reverse-engineering back to real face."],
          ["VO", "Voice Scrambling", "Audio pitch and timbre altered automatically. Voice fingerprint removed."],
          ["GEO", "No Geo-tagging", "All EXIF metadata stripped. Location services never accessed for uploads."],
          ["ENC", "End-to-End Encrypt", "Video encrypted before leaving device. Only decrypted in isolated GPU pipeline."],
          ["TTL", "Auto-Expiry", "Original upload deleted within 60 seconds of animation completion."],
        ].map(([icon, title, desc]) => (
          <div key={title} className="guarantee-item">
            <span className="guarantee-icon">{icon}</span>
            <div className="guarantee-text"><strong>{title}</strong>{desc}</div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const RoadmapPage = () => (
  <div className="roadmap-page">
    <div className="roadmap-title">DEVELOPMENT ROADMAP</div>
    <div className="roadmap-subtitle">From MVP to the world's most private social platform.</div>

    <div className="roadmap-metrics">
      {[["4", "Phases", "cyan"], ["18", "Features", "pink"], ["INF", "Privacy", "purple"], ["0", "Face Leaks", "gold"]].map(([num, label, color]) => (
        <div key={label} className="metric-card">
          <div className={`metric-num ${color}`}>{num}</div>
          <div className="metric-label">{label}</div>
        </div>
      ))}
    </div>

    <div className="roadmap-phases">
      {[
        {
          num: "01", label: "current", timeline: "Month 1-2",
          name: "MVP - Core Experience",
          desc: "Build the foundation: video upload, anime conversion pipeline, basic feed, and user accounts with zero PII storage.",
          features: [
            { label: "Video Upload Flow", status: "done" },
            { label: "CartoonGAN Integration", status: "done" },
            { label: "Basic Feed", status: "inprogress" },
            { label: "On-Device Face Detection", status: "inprogress" },
            { label: "User Accounts (anonymous)", status: "upcoming" },
          ]
        },
        {
          num: "02", label: "upcoming", timeline: "Month 3-4",
          name: "Social Layer",
          desc: "Likes, comments (text only), follows, notifications, and story-style short video strips.",
          features: [
            { label: "Like & Comment System", status: "upcoming" },
            { label: "Follow / Explore", status: "upcoming" },
            { label: "Stories (24hr)", status: "upcoming" },
            { label: "DMs (encrypted)", status: "upcoming" },
            { label: "Push Notifications", status: "upcoming" },
          ]
        },
        {
          num: "03", label: "upcoming", timeline: "Month 5-7",
          name: "Animation Quality & Styles",
          desc: "Multiple anime style choices, higher resolution output, real-time preview before publishing, audio voice morphing.",
          features: [
            { label: "Multi-Style GAN", status: "upcoming" },
            { label: "4K Anime Output", status: "upcoming" },
            { label: "Real-time Preview", status: "upcoming" },
            { label: "Voice Morphing AI", status: "upcoming" },
            { label: "Background Removal", status: "upcoming" },
          ]
        },
        {
          num: "04", label: "future", timeline: "Month 8-12",
          name: "Scale & Mobile",
          desc: "React Native mobile app, live streaming as anime, creator monetization with anonymous identity maintained throughout.",
          features: [
            { label: "iOS & Android Apps", status: "upcoming" },
            { label: "Live Anime Streaming", status: "upcoming" },
            { label: "Creator Fund", status: "upcoming" },
            { label: "Brand Partnerships", status: "upcoming" },
            { label: "Open Source SDK", status: "upcoming" },
          ]
        },
      ].map((phase) => (
        <div key={phase.num} className="phase-item">
          <div className={`phase-dot ${phase.label}`}>{phase.num}</div>
          <div className="phase-card">
            <div className="phase-header">
              <div className="phase-name">{phase.name}</div>
              <div className="phase-timeline">{phase.timeline}</div>
            </div>
            <div className="phase-desc">{phase.desc}</div>
            <div className="phase-features">
              {phase.features.map(f => (
                <span key={f.label} className={`feature-chip ${f.status === "done" ? "done" : f.status === "inprogress" ? "inprogress" : ""}`}>
                  {f.status === "done" ? "OK " : f.status === "inprogress" ? "IN " : "TO "}{f.label}
                </span>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

export default function App() {
  const [tab, setTab] = useState("feed");
  const [feedRefreshKey, setFeedRefreshKey] = useState(0);

  const TABS = [
    { key: "feed", label: "Feed" },
    { key: "upload", label: "Upload" },
    { key: "arch", label: "Architecture" },
    { key: "roadmap", label: "Roadmap" },
  ];

  const handlePostPublished = () => {
    setFeedRefreshKey((prev) => prev + 1);
    setTab("feed");
  };

  return (
    <>
      <style>{style}</style>
      <div className="app">
        <nav className="nav">
          <div className="logo">ANIME<span>FACE</span></div>
          <div className="nav-tabs">
            {TABS.map(t => (
              <button key={t.key} className={`nav-tab ${tab === t.key ? "active" : ""}`} onClick={() => setTab(t.key)}>
                {t.label}
              </button>
            ))}
          </div>
          <button className="nav-upload-btn" onClick={() => setTab("upload")}>+ Share Video</button>
        </nav>
        <div className="tab-content">
          {tab === "feed" && <FeedPage refreshKey={feedRefreshKey} />}
          {tab === "upload" && <UploadPage onPublished={handlePostPublished} />}
          {tab === "arch" && <ArchPage />}
          {tab === "roadmap" && <RoadmapPage />}
        </div>
      </div>
    </>
  );
}

