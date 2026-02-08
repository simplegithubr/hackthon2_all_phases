#!/usr/bin/env node

/**
 * WebSocket Test Client for Phase 5
 *
 * This script connects to the WebSocket service and listens for real-time task events.
 * Run this in a separate terminal while running the integration test.
 */

const WebSocket = require('ws');

// Configuration
const WS_URL = 'ws://localhost:8004';
const USER_ID = 'test-user-123';

console.log('========================================');
console.log('Phase 5 WebSocket Test Client');
console.log('========================================');
console.log('');
console.log(`Connecting to: ${WS_URL}`);
console.log(`User ID: ${USER_ID}`);
console.log('');

// Create WebSocket connection
const ws = new WebSocket(WS_URL);

// Connection opened
ws.on('open', function open() {
    console.log('✓ Connected to WebSocket server');
    console.log('');

    // Authenticate with user_id
    const authMessage = {
        type: 'auth',
        user_id: USER_ID
    };

    console.log('Sending authentication:', JSON.stringify(authMessage, null, 2));
    ws.send(JSON.stringify(authMessage));
    console.log('');
    console.log('Listening for events... (Press Ctrl+C to exit)');
    console.log('----------------------------------------');
    console.log('');
});

// Listen for messages
ws.on('message', function message(data) {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] Received event:`);

    try {
        const event = JSON.parse(data);
        console.log(JSON.stringify(event, null, 2));
    } catch (e) {
        console.log(data.toString());
    }

    console.log('----------------------------------------');
    console.log('');
});

// Handle errors
ws.on('error', function error(err) {
    console.error('✗ WebSocket error:', err.message);
    console.log('');
    console.log('Make sure to run port-forward first:');
    console.log('  kubectl port-forward svc/websocket-service 8004:8004');
    console.log('');
});

// Handle connection close
ws.on('close', function close() {
    console.log('✗ Connection closed');
    console.log('');
    process.exit(0);
});

// Handle process termination
process.on('SIGINT', function() {
    console.log('');
    console.log('Closing connection...');
    ws.close();
});
