# 502 Error Troubleshooting Guide

## What is a 502 Error?
A 502 Bad Gateway error means your application is crashing or failing to start properly on Render.

## Step 1: Check Render Logs
1. Go to your Render dashboard
2. Click on your service
3. Go to "Logs" tab
4. Look for error messages like:
   - Import errors
   - Memory errors
   - Port binding issues
   - Missing dependencies

## Step 2: Quick Fix - Deploy Minimal Version

### Option A: Use the fix script
```bash
python deploy_fix_502.py
```

### Option B: Manual steps
1. **Use minimal requirements:**
   ```bash
   cp requirements_minimal.txt requirements.txt
   ```

2. **Update render.yaml:**
   ```bash
   cp render_fixed.yaml render.yaml
   ```

3. **Deploy:**
   ```bash
   git add .
   git commit -m "Fix 502 error: use minimal requirements"
   git push
   ```

## Step 3: Test the Fix

1. **Wait 3-5 minutes** for deployment
2. **Test health endpoint:**
   ```
   https://your-app.onrender.com/health
   ```
3. **Check if it returns:**
   ```json
   {
     "status": "healthy",
     "message": "API is working"
   }
   ```

## Step 4: If Still Getting 502

### Check these common issues:

1. **Memory Issues:**
   - Render starter plan has 512MB limit
   - Large AI models can cause memory errors
   - Solution: Use WHISPER_MODEL_SIZE=tiny

2. **Import Errors:**
   - Missing dependencies
   - Python version mismatch
   - Solution: Check requirements.txt

3. **Port Issues:**
   - App not binding to correct port
   - Solution: Use `--port $PORT` in start command

4. **Startup Timeout:**
   - App takes too long to start
   - Solution: Optimize startup process

## Step 5: Gradual Feature Restoration

Once the minimal version works:

1. **Add back basic features:**
   ```bash
   # Restore full requirements
   git checkout HEAD~1 -- requirements.txt
   git add requirements.txt
   git commit -m "Restore full requirements"
   git push
   ```

2. **Monitor logs** for any new errors

3. **Test endpoints** one by one

## Step 6: Render Configuration

Make sure your render.yaml has:
```yaml
services:
  - type: web
    name: call-center-api
    env: python
    plan: starter  # More memory than free plan
    buildCommand: |
      pip install --upgrade pip
      pip install -r requirements.txt
    startCommand: python -m uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.18
      - key: PORT
        value: 10000
      - key: WHISPER_MODEL_SIZE
        value: tiny
      - key: ENVIRONMENT
        value: production
    healthCheckPath: /health
```

## Step 7: Environment Variables

Set these in Render dashboard:
- `PYTHON_VERSION`: 3.9.18
- `PORT`: 10000
- `WHISPER_MODEL_SIZE`: tiny
- `ENVIRONMENT`: production

## Step 8: Testing Commands

### Test locally first:
```bash
# Test minimal version
python test_minimal.py

# Test full version
python main.py

# Test imports
python -c "import main; print('Imports OK')"
```

### Test deployment:
```bash
# Health check
curl https://your-app.onrender.com/health

# Root endpoint
curl https://your-app.onrender.com/
```

## Common Error Messages and Solutions

### "ModuleNotFoundError"
- **Cause:** Missing dependency
- **Solution:** Add to requirements.txt

### "Out of memory"
- **Cause:** Too much memory usage
- **Solution:** Use smaller models, optimize code

### "Address already in use"
- **Cause:** Port binding issue
- **Solution:** Use `--port $PORT` in start command

### "ImportError"
- **Cause:** Python version mismatch
- **Solution:** Set PYTHON_VERSION=3.9.18

## Still Having Issues?

1. **Check Render status page:** https://status.render.com/
2. **Try different Python version**
3. **Use Render's support chat**
4. **Consider upgrading to paid plan** for more resources

## Success Indicators

Your deployment is working when:
- ✅ Health endpoint returns 200 OK
- ✅ No errors in Render logs
- ✅ Application starts within 30 seconds
- ✅ All endpoints respond correctly
