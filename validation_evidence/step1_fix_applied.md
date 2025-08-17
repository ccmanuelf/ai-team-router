# Step 1 Fix: Memory Timeout Threshold Adjustment

## Changes Made

**Health Monitor Fix:**
- 95% → 98% (only emergency at near-OOM)
- Removed 95% bypass that was forcing tiny model

**Memory Pressure Thresholds:**
- 85% → 90% (critical reduction from 30% to 20%)  
- 75% → 85% (high pressure from 20% to 10%)
- 60% → 75% (moderate from 15% to 5%)

## Expected Impact
- Large models (DeepCoder, Qwen, DeepSeek) should be selectable again
- Routing accuracy should improve from 40% to 70%+
- Health monitor only triggers at true emergency (98%+)

## Status: ✅ IMPLEMENTED
Router restarted with fix applied.
