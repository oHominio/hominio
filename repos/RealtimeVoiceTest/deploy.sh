#!/bin/bash

# Fly.io Deployment Script for RealtimeVoiceTest
# This script deploys the realtime voice chat application to Fly.io

set -e

echo "🚀 Starting Fly.io deployment for RealtimeVoiceTest..."

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl is not installed. Please install it first:"
    echo "   curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Check if logged in
if ! flyctl auth whoami &> /dev/null; then
    echo "❌ Not logged in to Fly.io. Please run:"
    echo "   flyctl auth login"
    exit 1
fi

# Set environment variables (you need to set these in Fly.io secrets)
if [ -z "$REDPILL_API_KEY" ]; then
    echo "⚠️  REDPILL_API_KEY not set. You'll need to set it as a Fly.io secret:"
    echo "   flyctl secrets set REDPILL_API_KEY=your_redpill_api_key_here"
fi

echo "📋 Deploying with configuration:"
echo "   App Name: realtime-voice-test"
echo "   Region: ord (Chicago)"
echo "   VM Size: a100-40gb"
echo "   TTS Engine: Kokoro"
echo "   LLM Provider: RedPill API (Phala/Llama 3.2)"

# Deploy to Fly.io
echo "🏗️  Starting deployment..."
flyctl deploy --app realtime-voice-test

echo "✅ Deployment completed!"
echo ""
echo "📡 Your app should be available at:"
echo "   https://realtime-voice-test.fly.dev"
echo ""
echo "🔑 Don't forget to set your secrets:"
echo "   flyctl secrets set REDPILL_API_KEY=your_redpill_api_key_here"
echo ""
echo "📊 Check app status:"
echo "   flyctl status --app realtime-voice-test"
echo ""
echo "📝 View logs:"
echo "   flyctl logs --app realtime-voice-test" 