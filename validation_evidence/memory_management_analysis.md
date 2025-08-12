# Memory Management Issues - Analysis

## Problems Identified

### 1. Model Selection Logic Flawed
- **Available memory**: 3.1GB
- **Selected**: mistral_versatile (4.9GB) in EDGE mode
- **Skipped**: Smaller models that would fit normally

### 2. Priority Order Wrong
Router skips appropriate models:
- granite_vision: 2.9GB (✅ fits)
- gemma_medium: 3.8GB (✅ fits) 
- Instead selects: mistral_versatile: 4.9GB (⚠️ edge mode)

### 3. Performance Impact
- Direct Ollama: 19.3s
- Through router: 25.3s (+6s overhead)
- Wrong model selection adds delay

## Root Cause
Model selection algorithm prioritizes wrong models for simple coding tasks.

## Required Fixes
1. Fix model priority for coding tasks
2. Ensure smaller models considered first
3. Test model unloading between requests
4. Validate memory calculations

---
*Analysis: 2025-08-12*