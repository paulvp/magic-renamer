#!/usr/bin/env python3
"""
MagicRenamer Web Interface
A web-based GUI for batch converting and renaming images
"""

from flask import Flask, render_template_string, request, jsonify, send_from_directory
import os
import subprocess
from pathlib import Path
import json
from PIL import Image
import smartcrop

app = Flask(__name__)
VERSION = "2.1.2-web"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>magic renamer v{{ version }}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #FFFEF9;
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container {
            max-width: 920px;
            margin: 0 auto;
        }
        .header {
            background: white;
            border: 3px solid black;
            border-radius: 24px;
            padding: 40px;
            text-align: center;
            box-shadow: 6px 6px 0px 0px rgba(0,0,0,1);
            margin-bottom: 30px;
        }
        .header h1 { 
            font-size: 3em; 
            font-weight: 800;
            margin-bottom: 8px;
            text-transform: lowercase;
            letter-spacing: -1px;
        }
        .header p { 
            color: #666;
            font-weight: 600;
            font-size: 0.9em;
        }
        .github-link {
            position: fixed;
            top: 16px;
            right: 16px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-top: 16px;
            padding: 10px 20px;
            background: white;
            border: 2px solid black;
            border-radius: 12px;
            text-decoration: none;
            color: black;
            font-weight: 600;
            font-size: 0.9em;
            box-shadow: 3px 3px 0px 0px rgba(0,0,0,1);
            transition: all 0.15s ease;
        }
        .github-link:hover {
            background: #FCD34D;
            transform: translate(2px, 2px);
            box-shadow: none;
        }
        .card {
            background: white;
            border: 3px solid black;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 6px 6px 0px 0px rgba(0,0,0,1);
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 24px;
        }
        label {
            display: block;
            font-weight: 700;
            margin-bottom: 10px;
            color: black;
            font-size: 0.95em;
        }
        .label-hint {
            color: #999;
            font-weight: 400;
            font-size: 0.9em;
        }
        input[type="text"], select {
            width: 100%;
            padding: 14px 18px;
            border: 3px solid black;
            border-radius: 16px;
            font-size: 15px;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            background: white;
            transition: all 0.15s ease;
        }
        input[type="text"]:focus, select:focus {
            outline: none;
            box-shadow: 4px 4px 0px 0px rgba(0,0,0,1);
            transform: translate(-2px, -2px);
        }
        select {
            cursor: pointer;
        }
        .input-with-button {
            display: flex;
            gap: 12px;
            align-items: stretch;
        }
        .input-with-button input {
            flex: 1;
        }
        .input-with-button .btn {
            white-space: nowrap;
            padding: 14px 24px;
        }
        .checkbox-wrapper {
            background: #FCD34D;
            border: 3px solid black;
            border-radius: 16px;
            padding: 16px 20px;
            display: inline-flex;
            align-items: center;
            cursor: pointer;
            box-shadow: 4px 4px 0px 0px rgba(0,0,0,1);
            transition: all 0.15s ease;
        }
        .checkbox-wrapper:hover {
            transform: translate(2px, 2px);
            box-shadow: none;
        }
        .checkbox-wrapper input {
            margin-right: 12px;
            width: 22px;
            height: 22px;
            cursor: pointer;
            accent-color: black;
        }
        .checkbox-wrapper label {
            margin: 0;
            cursor: pointer;
            font-weight: 600;
        }
        .file-list-container {
            background: white;
            border: 3px solid black;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 4px 4px 0px 0px rgba(0,0,0,1);
            position: relative;
        }
        .file-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 16px;
            max-height: 500px;
            overflow-y: auto;
            padding: 4px;
        }
        .file-list.empty {
            display: block;
        }
        .file-list::-webkit-scrollbar {
            width: 10px;
        }
        .file-list::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        .file-list::-webkit-scrollbar-thumb {
            background: black;
            border-radius: 10px;
        }
        .file-item {
            background: #FFFEF9;
            border: 2px solid black;
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.15s ease;
            cursor: pointer;
            position: relative;
        }
        .file-item:hover {
            background: #FCD34D;
            transform: translate(-2px, -2px);
            box-shadow: 3px 3px 0px 0px rgba(0,0,0,1);
        }
        .file-item.selected {
            border-color: #FCD34D;
            border-width: 3px;
        }
        .file-item-image {
            width: 100%;
            height: 100px;
            object-fit: cover;
            display: block;
            background: #e0e0e0;
        }
        .file-item-name {
            padding: 8px;
            font-weight: 500;
            font-size: 0.75em;
            text-align: center;
            word-break: break-word;
            line-height: 1.2;
        }
        .file-item-checkbox {
            position: absolute;
            top: 8px;
            left: 8px;
            width: 24px;
            height: 24px;
            cursor: pointer;
            accent-color: black;
            z-index: 10;
        }
        .selection-controls {
            display: flex;
            gap: 12px;
            margin-bottom: 16px;
            align-items: center;
            flex-wrap: wrap;
        }
        .btn {
            padding: 14px 28px;
            border: 3px solid black;
            border-radius: 16px;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.15s ease;
            font-family: 'Inter', sans-serif;
            box-shadow: 4px 4px 0px 0px rgba(0,0,0,1);
            background: white;
            color: black;
        }
        .btn:hover:not(:disabled) {
            transform: translate(2px, 2px);
            box-shadow: none;
        }
        .btn-primary {
            background: #FCD34D;
            color: black;
        }
        .btn-small {
            padding: 10px 20px;
            font-size: 14px;
        }
        .btn:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }
        .button-group {
            display: flex;
            gap: 12px;
            margin-top: 24px;
            flex-wrap: wrap;
        }
        .status {
            padding: 20px 24px;
            border-radius: 16px;
            margin-top: 20px;
            display: none;
            border: 3px solid black;
            font-weight: 600;
            box-shadow: 4px 4px 0px 0px rgba(0,0,0,1);
        }
        .status.success { background: #86efac; color: black; }
        .status.error { background: #fca5a5; color: black; }
        .status.info { background: #93c5fd; color: black; }
        .log-window {
            background: black;
            color: #00ff00;
            padding: 20px;
            border-radius: 16px;
            max-height: 320px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            margin-top: 20px;
            display: none;
            border: 3px solid black;
            box-shadow: 4px 4px 0px 0px rgba(0,0,0,1);
        }
        .log-window::-webkit-scrollbar {
            width: 10px;
        }
        .log-window::-webkit-scrollbar-track {
            background: #222;
        }
        .log-window::-webkit-scrollbar-thumb {
            background: #00ff00;
            border-radius: 5px;
        }
        .log-line { margin: 3px 0; }
        .log-success { color: #00ff00; }
        .log-error { color: #ff4444; }
        .log-info { color: #00d4ff; }
        .selection-count {
            background: white;
            border: 2px solid black;
            border-radius: 12px;
            padding: 8px 16px;
            font-weight: 700;
            font-size: 14px;
            margin-left: auto;
        }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #999;
            font-weight: 600;
            font-size: 1.1em;
        }
        .section-title {
            font-weight: 700;
            font-size: 1.1em;
            margin-bottom: 16px;
            text-transform: lowercase;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        .modal.active {
            display: flex;
        }
        .modal-content {
            background: white;
            border: 3px solid black;
            border-radius: 20px;
            padding: 30px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 8px 8px 0px 0px rgba(0,0,0,1);
        }
        .modal-header {
            font-weight: 700;
            font-size: 1.3em;
            margin-bottom: 20px;
            text-transform: lowercase;
        }
        .modal-close {
            float: right;
            font-size: 1.5em;
            cursor: pointer;
            font-weight: 700;
            line-height: 1;
        }
        .dir-item {
            padding: 12px 16px;
            margin: 6px 0;
            background: #FFFEF9;
            border: 2px solid black;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.15s ease;
            font-weight: 500;
        }
        .dir-item:hover {
            background: #FCD34D;
            transform: translate(-1px, -1px);
            box-shadow: 2px 2px 0px 0px rgba(0,0,0,1);
        }
        .dir-item.parent {
            background: #93c5fd;
        }
        .breadcrumb {
            background: white;
            border: 2px solid black;
            border-radius: 12px;
            padding: 12px 16px;
            margin-bottom: 16px;
            font-weight: 600;
            word-break: break-all;
        }
        .progress-bar {
            background: white;
            border: 3px solid black;
            border-radius: 16px;
            padding: 20px;
            margin-top: 20px;
            display: none;
            box-shadow: 4px 4px 0px 0px rgba(0,0,0,1);
        }
        .progress-bar-inner {
            background: #e0e0e0;
            border: 2px solid black;
            border-radius: 10px;
            height: 40px;
            overflow: hidden;
            position: relative;
        }
        .progress-bar-fill {
            background: linear-gradient(90deg, #FCD34D 0%, #FCA5A5 100%);
            height: 100%;
            width: 0%;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            color: black;
        }
        .progress-text {
            text-align: center;
            margin-top: 12px;
            font-weight: 600;
            font-size: 14px;
        }
        .resize-options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 12px;
        }
        .resize-option {
            background: white;
            border: 3px solid #ddd;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            cursor: pointer;
            transition: all 0.15s ease;
            font-weight: 600;
        }
        .resize-option:hover {
            border-color: black;
            transform: translate(-1px, -1px);
            box-shadow: 2px 2px 0px 0px rgba(0,0,0,1);
        }
        .resize-option.selected {
            background: #FCD34D;
            border-color: black;
            box-shadow: 3px 3px 0px 0px rgba(0,0,0,1);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✨ magic renamer</h1>
            <p>web interface</p>
            <a href="https://github.com/paulvp/magic-renamer" target="_blank" class="github-link">
                github
            </a>
        </div>
        
        <div class="card">
            <div class="form-group">
                <label>image directory</label>
                <div class="input-with-button">
                    <input type="text" id="directory" value="{{ current_dir }}" placeholder="enter directory path">
                    <button class="btn" onclick="openBrowser()">📁 browse</button>
                </div>
            </div>
            
            <div class="form-group">
                <label>naming prefix <span class="label-hint">(optional)</span></label>
                <input type="text" id="prefix" placeholder="e.g., photo, image, etc.">
            </div>
            
            <div class="form-group">
                <label>resize for AI training <span class="label-hint">(optional)</span></label>
                <div class="resize-options">
                    <div class="resize-option" data-size="" onclick="selectResize('')">
                        <div style="font-size: 1.2em;">✕</div>
                        <div>No resize</div>
                    </div>
                    <div class="resize-option" data-size="512" onclick="selectResize('512')">
                        <div style="font-size: 1.2em;">512</div>
                        <div>512×512</div>
                    </div>
                    <div class="resize-option" data-size="768" onclick="selectResize('768')">
                        <div style="font-size: 1.2em;">768</div>
                        <div>768×768</div>
                    </div>
                    <div class="resize-option" data-size="1024" onclick="selectResize('1024')">
                        <div style="font-size: 1.2em;">1024</div>
                        <div>1024×1024</div>
                    </div>
                    <div class="resize-option" data-size="2048" onclick="selectResize('2048')">
                        <div style="font-size: 1.2em;">2048</div>
                        <div>2048×2048</div>
                    </div>
                </div>
            </div>
            
            <div class="form-group">
                <label>crop mode <span class="label-hint">(when resizing)</span></label>
                <select id="cropMode">
                    <option value="center">Center crop (automatic)</option>
                    <option value="smart">Smart crop (AI-based, keeps important features)</option>
                </select>
            </div>
            
            <div class="form-group">
                <div class="checkbox-wrapper">
                    <input type="checkbox" id="skipConfirm">
                    <label for="skipConfirm">skip confirmation prompts</label>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="section-title">select images to process</div>
            <div class="selection-controls">
                <button class="btn btn-small" onclick="selectAll()">✓ select all</button>
                <button class="btn btn-small" onclick="deselectAll()">✗ deselect all</button>
                <div class="selection-count" id="selectionCount">0 selected</div>
            </div>
            <div class="file-list-container">
                <div class="file-list empty" id="fileList">
                    <div class="empty-state">click "scan directory" to load images</div>
                </div>
            </div>
        </div>
        
        <div class="button-group">
            <button class="btn" onclick="scanDirectory()">🔍 scan directory</button>
            <button class="btn btn-primary" onclick="processImages()">▶ process selected images</button>
        </div>
        
        <div class="progress-bar" id="progressBar">
            <div class="progress-bar-inner">
                <div class="progress-bar-fill" id="progressFill">0%</div>
            </div>
            <div class="progress-text" id="progressText">Processing...</div>
        </div>
        
        <div class="status" id="status"></div>
        <div class="log-window" id="logWindow"></div>
    </div>

    <!-- Directory Browser Modal -->
    <div class="modal" id="dirModal">
        <div class="modal-content">
            <div class="modal-header">
                <span class="modal-close" onclick="closeBrowser()">&times;</span>
                browse directories
            </div>
            <div class="breadcrumb" id="currentPath"></div>
            <div id="dirList"></div>
        </div>
    </div>

    <script>
        // MagicRenamer v2.1.2 - Cache busting fix - Timestamp: 2026-01-13-07:00
        let imageFiles = [];
        let currentBrowsePath = '{{ current_dir }}';
        let selectedResizeSize = '';
        
        function selectResize(size) {
            selectedResizeSize = size;
            document.querySelectorAll('.resize-option').forEach(function(opt) {
                if (opt.dataset.size === size) {
                    opt.classList.add('selected');
                } else {
                    opt.classList.remove('selected');
                }
            });
        }
        
        function openBrowser() {
            currentBrowsePath = document.getElementById('directory').value || '{{ current_dir }}';
            document.getElementById('dirModal').classList.add('active');
            loadDirectories(currentBrowsePath);
        }
        
        function closeBrowser() {
            document.getElementById('dirModal').classList.remove('active');
        }
        
        // Select "No resize" by default on page load
        window.addEventListener('DOMContentLoaded', function() {
            selectResize('');
        });
        
        async function loadDirectories(path) {
            try {
                const response = await fetch('/browse', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path: path })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    currentBrowsePath = data.current_path;
                    document.getElementById('currentPath').textContent = data.current_path;
                    
                    const dirList = document.getElementById('dirList');
                    dirList.innerHTML = '';
                    
                    // Add parent directory option
                    if (data.parent) {
                        const parentDiv = document.createElement('div');
                        parentDiv.className = 'dir-item parent';
                        parentDiv.textContent = '📁 .. (parent directory)';
                        parentDiv.onclick = function() { loadDirectories(data.parent); };
                        dirList.appendChild(parentDiv);
                    }
                    
                    // Add "Select this directory" button
                    const selectBtn = document.createElement('button');
                    selectBtn.className = 'btn btn-primary';
                    selectBtn.style.width = '100%';
                    selectBtn.style.marginBottom = '16px';
                    selectBtn.textContent = '✓ select this directory';
                    selectBtn.onclick = function() {
                        document.getElementById('directory').value = currentBrowsePath;
                        closeBrowser();
                        scanDirectory();
                    };
                    dirList.appendChild(selectBtn);
                    
                    // Add subdirectories
                    data.directories.forEach(function(dir) {
                        const dirDiv = document.createElement('div');
                        dirDiv.className = 'dir-item';
                        dirDiv.textContent = '📁 ' + dir;
                        dirDiv.onclick = function() { loadDirectories(data.current_path + '/' + dir); };
                        dirList.appendChild(dirDiv);
                    });
                    
                    if (data.directories.length === 0 && !data.parent) {
                        dirList.innerHTML += '<div class="empty-state">no subdirectories</div>';
                    }
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Error loading directories: ' + error.message);
            }
        }
        
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
            status.style.display = 'block';
        }
        
        function addLog(message, type) {
            type = type || '';
            const logWindow = document.getElementById('logWindow');
            logWindow.style.display = 'block';
            const line = document.createElement('div');
            line.className = 'log-line log-' + type;
            line.textContent = message;
            logWindow.appendChild(line);
            logWindow.scrollTop = logWindow.scrollHeight;
        }
        
        function clearLog() {
            document.getElementById('logWindow').innerHTML = '';
            document.getElementById('logWindow').style.display = 'none';
        }
        
        function updateProgress(current, total, message) {
            const progressBar = document.getElementById('progressBar');
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            
            progressBar.style.display = 'block';
            const percentage = Math.round((current / total) * 100);
            progressFill.style.width = percentage + '%';
            progressFill.textContent = percentage + '%';
            progressText.textContent = message || ('Processing ' + current + ' of ' + total + '...');
        }
        
        function hideProgress() {
            document.getElementById('progressBar').style.display = 'none';
        }
        
        function updateSelectionCount() {
            const checkboxes = document.querySelectorAll('.file-item input[type="checkbox"]');
            const selected = Array.from(checkboxes).filter(function(cb) { return cb.checked; }).length;
            document.getElementById('selectionCount').textContent = selected + ' of ' + checkboxes.length + ' selected';
        }
        
        function selectAll() {
            document.querySelectorAll('.file-item input[type="checkbox"]').forEach(function(cb) { cb.checked = true; });
            updateSelectionCount();
        }
        
        function deselectAll() {
            document.querySelectorAll('.file-item input[type="checkbox"]').forEach(function(cb) { cb.checked = false; });
            updateSelectionCount();
        }
        
        async function scanDirectory() {
            const directory = document.getElementById('directory').value;
            showStatus('Scanning directory...', 'info');
            
            try {
                const response = await fetch('/scan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ directory: directory })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    imageFiles = data.files;
                    renderFileList(data.files);
                    showStatus('Found ' + data.files.length + ' images', 'success');
                } else {
                    showStatus(data.error, 'error');
                }
            } catch (error) {
                showStatus('Error scanning directory: ' + error.message, 'error');
            }
        }
        
        function renderFileList(files) {
            const fileList = document.getElementById('fileList');
            
            if (files.length === 0) {
                fileList.innerHTML = '<div class="empty-state">No images found</div>';
                fileList.classList.add('empty');
                return;
            }
            
            const directory = document.getElementById('directory').value;
            fileList.classList.remove('empty');
            
            let html = '';
            files.forEach(function(file, idx) {
                html += '<div class="file-item" onclick="toggleFileSelection(' + idx + ')" id="file-' + idx + '">' +
                    '<input type="checkbox" class="file-item-checkbox" checked onchange="updateSelectionCount()" onclick="event.stopPropagation()">' +
                    '<img src="/image?dir=' + encodeURIComponent(directory) + '&file=' + encodeURIComponent(file) + '" class="file-item-image" alt="' + file + '">' +
                    '<div class="file-item-name">' + file + '</div>' +
                '</div>';
            });
            fileList.innerHTML = html;
            
            updateSelectionCount();
        }
        
        function toggleFileSelection(idx) {
            const checkbox = document.querySelectorAll('.file-item-checkbox')[idx];
            checkbox.checked = !checkbox.checked;
            updateSelectionCount();
        }
        
        async function processImages() {
            const directory = document.getElementById('directory').value;
            const prefix = document.getElementById('prefix').value;
            const resizeSize = selectedResizeSize;
            const cropMode = document.getElementById('cropMode').value;
            const skipConfirm = document.getElementById('skipConfirm').checked;
            
            const checkboxes = document.querySelectorAll('.file-item input[type="checkbox"]');
            const selectedFiles = Array.from(checkboxes)
                .map(function(cb, idx) { return cb.checked ? imageFiles[idx] : null; })
                .filter(function(f) { return f !== null; });
            
            if (selectedFiles.length === 0) {
                showStatus('No images selected', 'error');
                return;
            }
            
            if (!skipConfirm) {
                const naming = prefix ? (prefix + '-1.png, ' + prefix + '-2.png, ...') : '1.png, 2.png, ...';
                var msg = 'This will process ' + selectedFiles.length + ' selected images:';
                msg += String.fromCharCode(10) + String.fromCharCode(10);
                msg += '1. Convert to PNG format' + String.fromCharCode(10);
                
                if (resizeSize) {
                    msg += '2. Resize to ' + resizeSize + 'x' + resizeSize + ' (' + cropMode + ' crop)' + String.fromCharCode(10);
                    msg += '3. Delete original files' + String.fromCharCode(10);
                    msg += '4. Rename sequentially: ' + naming + String.fromCharCode(10) + String.fromCharCode(10);
                } else {
                    msg += '2. Delete original files' + String.fromCharCode(10);
                    msg += '3. Rename sequentially: ' + naming + String.fromCharCode(10) + String.fromCharCode(10);
                }
                
                msg += 'WARNING: This action cannot be undone!' + String.fromCharCode(10) + String.fromCharCode(10) + 'Continue?';
                
                if (!confirm(msg)) return;
            }
            
            clearLog();
            hideProgress();
            showStatus('Processing images...', 'info');
            updateProgress(0, selectedFiles.length, 'Starting...');
            
            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        directory: directory, 
                        prefix: prefix, 
                        files: selectedFiles,
                        resize_size: resizeSize,
                        crop_mode: cropMode
                    })
                });
                
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                
                while (true) {
                    const result = await reader.read();
                    if (result.done) break;
                    
                    const text = decoder.decode(result.value);
                    const lines = text.split(String.fromCharCode(10)).filter(function(l) { return l.trim(); });
                    
                    for (let i = 0; i < lines.length; i++) {
                        const line = lines[i];
                        if (line.startsWith('data: ')) {
                            const data = JSON.parse(line.substring(6));
                            
                            if (data.progress) {
                                updateProgress(data.current, data.total, data.message);
                            }
                            
                            if (data.log) {
                                if (data.log.startsWith('✓')) addLog(data.log, 'success');
                                else if (data.log.startsWith('✗')) addLog(data.log, 'error');
                                else if (data.log.startsWith('---')) addLog(data.log, 'info');
                                else addLog(data.log);
                            }
                            
                            if (data.complete) {
                                hideProgress();
                                showStatus('✓ Successfully processed ' + data.processed + ' images!', 'success');
                                await scanDirectory();
                            }
                            
                            if (data.error) {
                                hideProgress();
                                showStatus('Error: ' + data.error, 'error');
                            }
                        }
                    }
                }
            } catch (error) {
                hideProgress();
                showStatus('Error processing images: ' + error.message, 'error');
            }
        }
        
        // Auto-scan on load
        window.onload = function() { scanDirectory(); };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, 
                                 version=VERSION, 
                                 current_dir=os.getcwd())

@app.route('/favicon.ico')
def favicon():
    # Simple SVG favicon
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
        <rect width="32" height="32" fill="#FCD34D"/>
        <rect x="4" y="4" width="24" height="24" fill="white" stroke="black" stroke-width="2"/>
        <text x="16" y="20" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold">MR</text>
    </svg>'''
    return svg, 200, {'Content-Type': 'image/svg+xml'}

@app.route('/scan', methods=['POST'])
def scan_directory():
    data = request.json
    directory = data.get('directory', os.getcwd())
    
    if not os.path.isdir(directory):
        return jsonify({'success': False, 'error': 'Invalid directory path'})
    
    extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff', '.tif']
    
    try:
        files = []
        for file in os.listdir(directory):
            if any(file.lower().endswith(ext) for ext in extensions):
                if not file.startswith('temp_'):
                    files.append(file)
        
        # Natural sort (numeric sort for numbers in filenames)
        import re
        def natural_sort_key(s):
            return [int(text) if text.isdigit() else text.lower()
                    for text in re.split('([0-9]+)', s)]
        
        files.sort(key=natural_sort_key)
        return jsonify({'success': True, 'files': files})
    except PermissionError:
        return jsonify({'success': False, 'error': 'Permission denied'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/browse', methods=['POST'])
def browse_directory():
    data = request.json
    path = data.get('path', os.getcwd())
    
    try:
        # Normalize and resolve path
        path = os.path.abspath(os.path.expanduser(path))
        
        if not os.path.isdir(path):
            return jsonify({'success': False, 'error': 'Invalid directory path'})
        
        # Get subdirectories only
        directories = []
        try:
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    directories.append(item)
        except PermissionError:
            pass
        
        # Get parent directory
        parent = os.path.dirname(path) if path != '/' else None
        
        return jsonify({
            'success': True,
            'current_path': path,
            'parent': parent,
            'directories': directories
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/image')
def serve_image():
    """Serve image files for preview"""
    try:
        directory = request.args.get('dir', '')
        filename = request.args.get('file', '')
        
        if not directory or not filename:
            return '', 404
        
        # Normalize the directory path
        directory = os.path.abspath(os.path.expanduser(directory))
        
        # Security check - ensure the file exists and is in the specified directory
        file_path = os.path.join(directory, filename)
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return '', 404
        
        return send_from_directory(directory, filename)
    except Exception as e:
        return '', 404

def resize_center_crop(input_file, output_file, target_size):
    """Resize and center crop image"""
    try:
        # Get dimensions
        result = subprocess.run(
            ['identify', '-format', '%wx%h', input_file],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return False
        
        dims = result.stdout.strip().split('x')
        width, height = int(dims[0]), int(dims[1])
        
        # Calculate crop dimensions
        if width > height:
            # Wider - crop width
            new_width = height
            offset_x = (width - new_width) // 2
            crop_geometry = f"{new_width}x{height}+{offset_x}+0"
        else:
            # Taller - crop height
            new_height = width
            offset_y = (height - new_height) // 2
            crop_geometry = f"{width}x{new_height}+0+{offset_y}"
        
        # Crop and resize
        result = subprocess.run(
            ['magick', input_file, '-crop', crop_geometry, '-resize', 
             f'{target_size}x{target_size}', output_file],
            capture_output=True, timeout=30
        )
        
        return result.returncode == 0
    except Exception:
        return False

def resize_smart_crop(input_file, output_file, target_size):
    """Resize with AI-based smart cropping using attention detection"""
    try:
        # Open image with PIL
        img = Image.open(input_file)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Initialize smartcrop
        sc = smartcrop.SmartCrop()
        
        # Calculate crop area using ML attention detection
        result = sc.crop(img, target_size, target_size)
        
        # Get the best crop coordinates
        crop_box = result['top_crop']
        x, y, width, height = crop_box['x'], crop_box['y'], crop_box['width'], crop_box['height']
        
        # Crop the image
        cropped = img.crop((x, y, x + width, y + height))
        
        # Resize to exact target size
        final = cropped.resize((target_size, target_size), Image.LANCZOS)
        
        # Save as PNG
        final.save(output_file, 'PNG', optimize=True)
        
        return True
    except Exception as e:
        # Fallback to center crop if smart crop fails
        try:
            result = subprocess.run(
                ['magick', input_file, 
                 '-resize', f'{target_size}x{target_size}^',
                 '-gravity', 'center',
                 '-extent', f'{target_size}x{target_size}',
                 output_file],
                capture_output=True, timeout=30
            )
            return result.returncode == 0
        except Exception:
            return False

@app.route('/process', methods=['POST'])
def process_images():
    data = request.json
    directory = data.get('directory', os.getcwd())
    prefix = data.get('prefix', '')
    selected_files = data.get('files', [])
    resize_size = data.get('resize_size', '')
    crop_mode = data.get('crop_mode', 'center')
    
    def generate():
        if not os.path.isdir(directory):
            yield f"data: {json.dumps({'error': 'Invalid directory path'})}\n\n"
            return
        
        if not selected_files:
            yield f"data: {json.dumps({'error': 'No files selected'})}\n\n"
            return
        
        try:
            os.chdir(directory)
            
            # Check ImageMagick
            try:
                subprocess.run(['magick', '--version'], capture_output=True, timeout=5)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                yield f"data: {json.dumps({'error': 'ImageMagick not found'})}\n\n"
                return
            
            # Step 1: Convert (and optionally resize)
            if resize_size:
                yield f"data: {json.dumps({'log': f'--- Converting and resizing to {resize_size}x{resize_size} ---'})}\n\n"
            else:
                yield f"data: {json.dumps({'log': '--- Converting to PNG format ---'})}\n\n"
            
            i = 1
            temp_files = []
            total = len(selected_files)
            
            for idx, filename in enumerate(selected_files):
                file_path = Path(filename)
                if not file_path.exists():
                    yield f"data: {json.dumps({'log': f'✗ File not found: {filename}'})}\n\n"
                    continue
                
                temp_name = f"temp_{i:04d}.png"
                
                # Update progress
                yield f"data: {json.dumps({'progress': True, 'current': idx + 1, 'total': total, 'message': f'Processing {filename}'})}\n\n"
                
                try:
                    if resize_size:
                        if crop_mode == 'smart':
                            success = resize_smart_crop(str(file_path), temp_name, int(resize_size))
                        else:
                            success = resize_center_crop(str(file_path), temp_name, int(resize_size))
                    else:
                        result = subprocess.run(
                            ['magick', str(file_path), temp_name],
                            capture_output=True, text=True, timeout=30
                        )
                        success = result.returncode == 0
                    
                    if success:
                        yield f"data: {json.dumps({'log': f'✓ Processed: {filename}'})}\n\n"
                        temp_files.append((filename, temp_name))
                        i += 1
                    else:
                        yield f"data: {json.dumps({'log': f'✗ Failed: {filename}'})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'log': f'✗ Error: {filename} - {str(e)}'})}\n\n"
            
            # Step 2: Remove originals
            yield f"data: {json.dumps({'log': ''})}\n\n"
            yield f"data: {json.dumps({'log': '--- Removing original files ---'})}\n\n"
            
            for idx, (original_file, temp_file) in enumerate(temp_files):
                yield f"data: {json.dumps({'progress': True, 'current': idx + 1, 'total': len(temp_files), 'message': 'Removing originals'})}\n\n"
                try:
                    Path(original_file).unlink()
                    yield f"data: {json.dumps({'log': f'✓ Removed: {original_file}'})}\n\n"
                except Exception:
                    yield f"data: {json.dumps({'log': f'✗ Failed to remove: {original_file}'})}\n\n"
            
            # Step 3: Rename
            yield f"data: {json.dumps({'log': ''})}\n\n"
            yield f"data: {json.dumps({'log': '--- Renaming to sequential numbers ---'})}\n\n"
            
            i = 1
            for idx, (original_file, temp_file) in enumerate(temp_files):
                new_name = f"{prefix}-{i}.png" if prefix else f"{i}.png"
                
                yield f"data: {json.dumps({'progress': True, 'current': idx + 1, 'total': len(temp_files), 'message': 'Renaming files'})}\n\n"
                
                try:
                    Path(temp_file).rename(new_name)
                    yield f"data: {json.dumps({'log': f'✓ {temp_file} -> {new_name}'})}\n\n"
                    i += 1
                except Exception:
                    yield f"data: {json.dumps({'log': f'✗ Failed: {temp_file}'})}\n\n"
            
            yield f"data: {json.dumps({'complete': True, 'processed': len(temp_files)})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return app.response_class(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    print("✨ MagicRenamer Web Interface")
    print(f"Version: {VERSION}")
    print("\n🌐 Starting server at http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    app.run(host='0.0.0.0', port=5000, debug=False)