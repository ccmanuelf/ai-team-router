# Phase 4: Benchmarking Plan

## Objective
Document realistic performance data comparing local models vs cloud service claims.

## Testing Framework

### Phase 4A: Model Performance (Individual)
**Test each available model:**
- Response time (cold start + warm)
- Memory usage during operation
- Token generation speed
- Quality assessment (1-10 scale)

**Test prompts:**
1. Simple: "Write a Python function to sort a list"
2. Medium: "Create a Vue 3 component with form validation"  
3. Complex: "Design a Laravel API with authentication and caching"
4. Excel: "Generate VBA for 150k row inventory reconciliation"
5. Vision: "Analyze uploaded screenshot for UI elements"

### Phase 4B: Router Intelligence
**Test task routing accuracy:**
- Vue/React → Should select deepcoder_primary
- Excel/VBA → Should select qwen_analyst
- Laravel/PHP → Should select deepseek_legacy
- Vision → Should select granite_vision

**Metrics:**
- Routing accuracy (correct model selected)
- Fallback behavior under memory pressure
- Edge mode performance degradation

### Phase 4C: End-to-End Workflows
**Real-world scenarios:**
1. Full Vue component development (design → code → test)
2. Excel data processing (150k rows)
3. Laravel API creation with database
4. Multi-tool usage (search + code + excel)

### Phase 4D: Cloud Comparison
**Compare against documented claims:**
- GPT-4: 3-5s response time
- Claude: 5-7s for Excel tasks
- Copilot: 2-3s for Laravel
- Sonnet 3.5: 4-5s code review

## Execution Strategy

### Immediate (Phase 4A)
Test 3-4 available models with memory constraints

### When Memory Available (Phase 4B)
Test qwen_analyst + larger models

### Comprehensive (Phase 4C-D)
Full workflow testing + cloud comparison

## Evidence Collection
- Response times (automated timing)
- Memory usage logs
- Quality scoring (manual assessment)
- Routing decision logs
- Failure/fallback documentation

**Goal:** Realistic performance documentation vs marketing claims.
