# Troubleshooting Guide

## Common Issues

### Out of Memory Errors

**Symptoms:**
- Models fail to load
- System becomes unresponsive

**Solutions:**
1. Close other applications
2. Use smaller models
3. Enable emergency mode
4. Restart Ollama service

### Model Not Found

**Symptoms:**
- Error: model not found

**Solutions:**
```bash
# Pull missing model
ollama pull model_name

# Verify installation
ollama list
```

### Slow Response Times

**Causes:**
- High memory pressure
- Wrong model selected
- Large context

**Solutions:**
1. Check memory usage
2. Use appropriate model for task
3. Reduce context size

### API Connection Errors

**Check:**
```bash
# Is Ollama running?
pgrep ollama

# Is router running?
curl http://localhost:11435/health

# Check logs
tail -f logs/router.log
```

### Emergency Recovery

```bash
# Kill all processes
pkill ollama
pkill python

# Clear cache
rm -rf ~/.ollama/models/.cache

# Restart
ollama serve &
python src/ai_team_router.py
```