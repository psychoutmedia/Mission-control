# LLM Multi-Modal Capabilities

## What is Multi-Modal?

LLMs that process multiple types of input:
- Text (always)
- Images (Vision)
- Audio (Speech)
- Video
- Documents (PDF)

## Major Models

| Model | Vision | Audio | Video |
|-------|--------|-------|-------|
| GPT-4V | ✅ | ✅ | - |
| Claude 3 | ✅ | - | - |
| Gemini | ✅ | ✅ | ✅ |
| LLaVA | ✅ | - | - |
| GPT-4o | ✅ | ✅ | - |

## Use Cases

### Vision
- Image captioning
- Visual QA
- Document understanding
- Chart analysis

### Audio
- Speech transcription
- Audio understanding
- Text-to-speech

### Video
- Video understanding
- Frame analysis

## For Agents

Multi-modal enables:
- See screenshots
- Read documents
- Process audio input
- Richer interactions

## Implementation

```python
# OpenAI vision
response = client.chat.completions.create(
    model="gpt-4-vision",
    messages=[{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": "..."}},
            {"type": "text", "text": "What's in this image?"}
        ]
    }]
)
```

## Cost

Multi-modal is more expensive:
- Image input: ~$0.01-0.03 per image
- Audio: ~$0.01 per minute
- Check provider pricing
