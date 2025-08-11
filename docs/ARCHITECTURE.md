# Architecture Documentation

## System Overview

The AI Team Router is a sophisticated orchestration system that manages 11 specialized AI models on a single M3 Pro MacBook with 18GB RAM.

## Core Components

### 1. Model Router (ai_team_router.py)
- Intelligent task analysis
- Dynamic model selection
- Memory management
- Fallback mechanisms

### 2. Tool Integration (tools.py)
- Web search (DuckDuckGo, Tavily, Google)
- Code execution (sandboxed)
- Excel/VBA optimization
- File analysis
- Vision/OCR capabilities

### 3. Memory Management
- M3 Pro unified memory optimization
- Smart model unloading
- Emergency fallback to minimal models
- Pressure-based scaling

## Model Selection Algorithm

```python
# Scoring factors:
- Domain match: +10-15 points
- Complexity alignment: +5 points
- Tool requirements: +2 per tool
- Memory efficiency: +2 for simple tasks
- Performance rating: +0.5 * rating
```

## API Endpoints

- POST `/api/chat` - Main chat endpoint
- GET `/api/team/status` - System status
- GET `/api/team/members` - Team details
- POST `/api/team/switch` - Manual model switch
- GET `/health` - Health check

## Data Flow

1. Request arrives at `/api/chat`
2. Task analyzer evaluates requirements
3. Model selector chooses best member
4. Memory manager ensures availability
5. Request routed to Ollama
6. Response returned with metadata