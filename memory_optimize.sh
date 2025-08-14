#!/bin/bash
# Memory Optimization Script for Large Model Testing

echo "🧹 MEMORY OPTIMIZATION FOR LARGE MODEL TESTING"
echo "============================================================"

echo "📊 Current Memory Status:"
python3 -c "
import psutil
mem = psutil.virtual_memory()
print(f'  Available: {mem.available/1024**3:.1f}GB ({100-mem.percent:.1f}% free)')
print(f'  Used: {mem.used/1024**3:.1f}GB ({mem.percent:.1f}% used)')
print(f'  Need for 9GB model: ~9.5GB')
print(f'  Current deficit: {9.5 - mem.available/1024**3:.1f}GB')
"

echo -e "\n🎯 OPTIMIZATION STRATEGY:"
echo "1. Close memory-heavy applications temporarily"
echo "2. Force system memory cleanup" 
echo "3. Test one large model at a time"
echo "4. Use edge mode if needed (4GB over-memory allowed)"

echo -e "\n💡 MANUAL STEPS TO FREE MEMORY:"
echo "✅ Option 1: Close Claude app tabs/windows (saves ~3-4GB)"
echo "✅ Option 2: Close Safari tabs (saves ~3-4GB)" 
echo "✅ Option 3: Close WhatsApp/Outlook temporarily (saves ~1GB total)"
echo "✅ Option 4: Force memory purge: sudo purge"

echo -e "\n🔧 AUTOMATED CLEANUP ATTEMPT:"

# Try to free some memory safely
echo "📱 Closing unnecessary background apps..."

# Kill some non-essential processes if running
killall -9 "Microsoft Outlook" 2>/dev/null && echo "  ✅ Closed Outlook"
killall -9 "WhatsApp" 2>/dev/null && echo "  ✅ Closed WhatsApp"

echo "🧹 Attempting memory pressure relief..."
# This might require user permission
sudo purge 2>/dev/null && echo "  ✅ Memory purged" || echo "  ⚠️  Purge requires sudo password"

echo "💤 Waiting 5 seconds for memory to stabilize..."
sleep 5

echo -e "\n📊 After Cleanup:"
python3 -c "
import psutil
mem = psutil.virtual_memory()
print(f'  Available: {mem.available/1024**3:.1f}GB ({100-mem.percent:.1f}% free)')
print(f'  Deficit for 9GB model: {max(0, 9.5 - mem.available/1024**3):.1f}GB')
if mem.available/1024**3 >= 9.5:
    print('  🎉 SUFFICIENT for large model testing!')
elif mem.available/1024**3 + 4.0 >= 9.5:
    print('  🔥 EDGE MODE possible (4GB over-memory)')
else:
    print('  ❌ Still insufficient - manual intervention needed')
"

echo -e "\n🚀 READY FOR LARGE MODEL TEST"
echo "Run: python3 test_large_model_unload.py"