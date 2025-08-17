# Phase 4A Collaborative Testing Guide

## 🎯 Ready for Execution

**Computer restart**: ✅ Completed  
**Scripts created**: ✅ Ready for collaborative testing

## 📋 Execution Sequence

### Option 1: Comprehensive Analysis (Recommended)
```bash
# Run full collaborative validation with detailed memory monitoring
python3 phase4a_collaborative_validation.py
```

**What this does:**
1. **Memory Unload Investigation**: Tests single DeepCoder load/unload cycle with 90s memory monitoring
2. **Router Switching Test**: Tests Vue.js → Excel VBA → Laravel routing with memory tracking
3. **Generates comprehensive report**: Saves detailed JSON results for analysis

**Expected duration**: 15-20 minutes  
**Output**: `validation_evidence/phase4a_collaborative_validation.json`

### Option 2: Quick Memory Test (Fast preliminary check)
```bash
# Quick single model unload test
python3 quick_memory_test.py
```

**What this does:**
1. Loads DeepCoder model
2. Monitors unload for 60 seconds
3. Reports memory release effectiveness

**Expected duration**: 3-5 minutes  
**Use case**: Quick verification before full test

### Option 3: Analyze Previous Results
```bash
# Analyze existing results
python3 analyze_memory_results.py
```

**What this does:**
1. Finds latest collaborative validation results
2. Generates detailed analysis report
3. Provides actionable recommendations

## 🔍 Key Investigations

### Memory Unload Timing
- **Current hypothesis**: 10s timeout insufficient for 9GB models
- **Expected finding**: 30-60+ seconds needed for complete memory release
- **Evidence**: M3 Pro ARM architecture memory management timing

### Router Model Switching  
- **Current hypothesis**: Models accumulating instead of unloading
- **Expected finding**: Cascading failures due to memory constraints
- **Evidence**: Vue.js works → Excel VBA falls back to tiny model

### Memory Monitoring Accuracy
- **Current hypothesis**: psutil may not reflect unreleased memory
- **Expected finding**: Memory calculations based on inaccurate readings
- **Evidence**: Router selecting models that can't actually load

## 📊 Success Criteria

### Phase 4A Pass Requirements
- **Routing accuracy**: ≥70% (currently ~50%)
- **Memory management**: Effective model unloading
- **Model selection**: Appropriate models for each domain:
  - Vue.js → DeepCoder (9GB)
  - Excel VBA → Qwen (9GB) 
  - Laravel → DeepSeek (8.9GB)

### Failure Indicators
- **Memory accumulation**: Models not unloading properly
- **Forced fallbacks**: Router using Gemma Tiny instead of appropriate models
- **Timeout errors**: Large models failing to respond within timeouts

## 🔧 Expected Fixes Based on Results

### If Memory Unload Fails
1. **Increase timeout**: 10s → 60s+ for large models
2. **Enhance unload mechanism**: Different Ollama commands
3. **Add verification**: Monitor actual memory release

### If Memory Unload Works
1. **Investigate routing logic**: Model selection algorithms
2. **Check memory calculations**: _get_available_memory_gb() accuracy
3. **Review fallback logic**: Better intermediate model selection

## 🤝 Collaborative Protocol

1. **Human executes** scripts locally on M3 Pro hardware
2. **Real memory behavior** observed (no sandbox limitations)
3. **Claude analyzes** results and generates targeted fixes
4. **Iterative improvement** based on actual data

## 🚀 Ready to Proceed

**All scripts are prepared and ready for execution.**

Choose your preferred approach:
- **Comprehensive** (recommended): `python3 phase4a_collaborative_validation.py`
- **Quick check**: `python3 quick_memory_test.py`  
- **Analyze existing**: `python3 analyze_memory_results.py`

The collaborative testing will provide the real data needed to identify and fix the memory management issues blocking Phase 4A completion.
