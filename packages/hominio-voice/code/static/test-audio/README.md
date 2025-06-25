# Test Audio Files

This directory contains pre-recorded audio prompts for load testing the voice chat system.

## File Requirements

- **Format**: WAV, 16-bit PCM, 24kHz sample rate, mono
- **Naming**: Use descriptive names like `prompt_3s.wav`, `prompt_5s.wav`, etc.
- **Duration**: Various lengths (3s, 5s, 8s, 10s, 15s, 20s) for testing different scenarios

## Recommended Test Prompts

### 3 seconds
- "Hello, how are you today?"
- "What's the weather like?"
- "Can you help me?"

### 5 seconds  
- "Can you help me find information about the weather?"
- "I need assistance with my computer problem."
- "What are some good restaurants nearby?"

### 8 seconds
- "I'm looking for a good restaurant recommendation in the downtown area."
- "Could you explain what machine learning is in simple terms?"
- "I'm having trouble setting up my new phone device."

### 10 seconds
- "Could you please explain how machine learning algorithms work in simple terms?"
- "I'm planning a trip to Europe and need some travel advice for first time visitors."
- "Can you help me understand the differences between various programming languages?"

### 15 seconds
- "I'm planning a vacation to Europe next summer and need advice on the best places to visit, especially for historical sites."
- "I'm trying to learn a new programming language and would like some guidance on which one would be best for beginners."
- "Could you help me understand how to set up a home network with multiple devices including computers, phones, and smart home devices?"

### 20 seconds
- "I've been having trouble with my computer lately, it keeps freezing when I try to run multiple applications, and I'm wondering if you could help me troubleshoot this issue."
- "I'm interested in starting a small business from home and would like to know about the legal requirements, tax considerations, and basic steps to get started."
- "I'm trying to improve my cooking skills and would love some advice on essential techniques, must-have kitchen tools, and some beginner-friendly recipes to try."

## Audio Sources

### Free Sources:
1. **Mozilla Common Voice**: https://commonvoice.mozilla.org/
2. **LibriSpeech**: http://www.openslr.org/12/
3. **VCTK Corpus**: https://datashare.ed.ac.uk/handle/10283/3443

### TTS Generation:
- Use ElevenLabs, Azure TTS, or Google TTS to generate consistent test audio
- Ensure consistent volume levels across all files
- Use different voices for variety in testing

## File Conversion

If you have audio in other formats, convert using FFmpeg:

```bash
# Convert to required format
ffmpeg -i input.mp3 -ar 24000 -ac 1 -sample_fmt s16 output.wav

# Trim to specific duration
ffmpeg -i input.wav -t 5 -ar 24000 -ac 1 -sample_fmt s16 prompt_5s.wav
```

## Load Testing Usage

The load tester will randomly select from available audio files and simulate:
- Multiple concurrent users (1-30)
- Random prompt intervals (3-6 times per 3 minutes)
- Realistic audio streaming timing
- Response latency measurement

Place your audio files in this directory and they will be automatically available to the load testing system. 