# Memory Management Plan - Updated

## Current Status: RESTART FRESH REQUIRED

### Issue Analysis Summary
**Problem:** Model unloading mechanism failing, causing memory accumulation and forcing router to fallback to tiny models instead of appropriate domain-specific models.

**Evidence:**
- Excel VBA → Gemma Tiny (should be Qwen/Granite/Mistral)  
- Vue.js → Timeout error (likely due to memory pressure)
- Routing accuracy: 50% (below 70% target)
- Models accumulating in memory instead of proper unloading

### Root Cause Assessment
**NOT a routing logic issue** - Domain detection working correctly:
- ✅ Excel VBA correctly identified as "enterprise" domain
- ✅ Vue.js correctly identified as "coding" domain  
- ✅ Manual model test (DeepCoder direct) works perfectly

**IS a memory management issue** - Unloading mechanism failing:
- ❌ Previous models not releasing memory properly
- ❌ 10s unload timeout insufficient for large models
- ❌ Memory pressure forcing emergency fallbacks

## New Testing Protocol: COLLABORATIVE EXECUTION

### Rationale for Change
**Sandbox Environment Issues:**
- Shell execution timeouts preventing proper testing
- False positive/negative results due to execution constraints
- Inability to accurately measure router performance in constrained environment

**Collaborative Testing Benefits:**
- Eliminates sandbox interference
- Provides accurate performance data  
- Maintains proper testing rigor
- Allows real-time debugging and validation

### Collaborative Testing Workflow

**Phase 1: Script Creation**
- Claude writes comprehensive validation scripts for each Phase 4 test
- Scripts include detailed logging, error handling, and result capture
- Each script targets specific routing accuracy metrics
- Scripts save results to structured JSON files for analysis

**Phase 2: Local Execution**  
- Human runs scripts in native terminal environment
- No sandbox limitations or artificial timeouts
- Real memory management and model loading behavior
- Captures complete stdout/stderr output

**Phase 3: Results Analysis**
- Claude reads generated log files and JSON results
- Analyzes routing accuracy, response times, model selection
- Validates against phase-specific success criteria
- Identifies specific issues if phase fails

**Phase 4: Iterative Improvement**
- If phase fails: Claude creates targeted fixes
- If phase passes: Proceed to next phase
- Human provides terminal output for verification when needed
- Maintain continuous progress tracking

## Memory Management Strategy - Revised

### Immediate Actions
1. **Restart computer** - Clear all model memory accumulation
2. **Fresh Phase 4 testing** - Begin with clean memory state
3. **Enhanced logging** - Monitor memory usage throughout tests
4. **Incremental validation** - Test one model at a time initially

### Memory Optimization Priorities
1. **Validate unloading works** - Single model load/unload cycles
2. **Test memory monitoring** - Verify available memory calculations
3. **Validate routing logic** - Ensure domain detection functional
4. **Test edge mode behavior** - Memory deficit handling
5. **Full integration test** - Multi-model switching scenarios

### Success Metrics - Phase 4A
- **Routing Accuracy:** ≥70% correct model selection
- **Memory Management:** Successful model switching without accumulation
- **Response Success:** ≥75% successful API responses  
- **Domain Detection:** 100% correct domain identification

## Testing Phases - Collaborative Execution Plan

### Phase 4A: Routing Accuracy Validation
**Script:** `validate_phase4a_routing.py`
**Tests:** Vue.js→DeepCoder, Excel VBA→Qwen, Laravel→DeepSeek, Simple→Any
**Success Criteria:** ≥70% routing accuracy + ≥75% response success
**Memory Focus:** Model selection and basic switching

### Phase 4B: Router Intelligence Testing  
**Script:** `validate_phase4b_intelligence.py`
**Tests:** Complex prompts, edge cases, domain boundary conditions
**Success Criteria:** Intelligent routing decisions, appropriate fallbacks
**Memory Focus:** Memory-aware model selection

### Phase 4C: Performance & Optimization
**Script:** `validate_phase4c_performance.py` 
**Tests:** Response times, memory efficiency, concurrent requests
**Success Criteria:** Acceptable performance metrics
**Memory Focus:** Memory optimization and resource usage

### Phase 4D: Edge Cases & Reliability
**Script:** `validate_phase4d_reliability.py`
**Tests:** Error handling, memory pressure scenarios, failover behavior
**Success Criteria:** Graceful degradation and error recovery
**Memory Focus:** Memory pressure handling and emergency fallbacks

## Technical Implementation Notes

### Script Requirements
- **Comprehensive error handling** - Catch and log all failure modes
- **Detailed memory monitoring** - Track available memory throughout tests
- **Model switching validation** - Verify previous models properly unloaded
- **Response time measurement** - Track performance across model sizes
- **JSON result export** - Structured data for programmatic analysis
- **Human-readable output** - Clear terminal feedback during execution

### Validation Criteria
- **Quantitative metrics** - Routing accuracy percentages, response times
- **Qualitative assessment** - Response quality, appropriate model selection
- **Memory behavior** - Proper unloading, memory release patterns
- **Error handling** - Graceful failures, meaningful error messages

### Progress Tracking
- **Phase completion status** - Clear pass/fail criteria for each phase
- **Issue identification** - Specific problems found and resolution status  
- **Performance metrics** - Measurable improvements across phases
- **Memory optimization** - Tracking memory management improvements

## Current State Summary

**Memory Management Status:** BROKEN - requires fresh restart
**Routing Logic Status:** PARTIALLY VALIDATED - domain detection working
**Testing Approach:** CHANGED to collaborative execution model
**Phase 4A Status:** FAILED - 50% routing accuracy due to memory issues

**Next Actions:**
1. Restart computer for clean memory state
2. Create Phase 4A collaborative validation script
3. Execute script locally in terminal
4. Analyze results and proceed based on findings

This approach ensures accurate testing without sandbox interference while maintaining rigorous validation standards.
