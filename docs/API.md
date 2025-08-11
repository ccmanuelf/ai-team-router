# API Reference

## Base URL
```
http://localhost:11435
```

## Endpoints

### POST /api/chat
Main endpoint for AI interactions.

**Request:**
```json
{
  "prompt": "Create a Vue component",
  "context": {
    "temperature": 0.7,
    "priority": "normal"
  }
}
```

**Response:**
```json
{
  "response": "Generated content...",
  "metadata": {
    "model": "deepcoder:latest",
    "member": "DeepCoder Prime",
    "elapsed_time": 4.2,
    "memory_used_gb": 9.0
  }
}
```

### GET /api/team/status
Get current system status.

**Response:**
```json
{
  "active_member": "deepcoder_primary",
  "team_size": 11,
  "system": {
    "platform": "M3 Pro",
    "total_memory_gb": 18.0,
    "available_memory_gb": 4.5,
    "memory_pressure": 75.0
  }
}
```

### GET /api/team/members
List all team members.

### POST /api/team/switch
Manually switch to specific model.

**Request:**
```json
{
  "member_id": "qwen_analyst"
}
```