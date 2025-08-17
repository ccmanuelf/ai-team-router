def _execute_python(code: str) -> str:
    """Execute Python code safely"""
    try:
        if any(dangerous in code.lower() for dangerous in ['import os', 'subprocess', 'exec', 'eval']):
            return "Code execution blocked: potentially unsafe operations detected"
        
        # Create safe namespace
        safe_globals = {
            '__builtins__': {
                'print': print, 'len': len, 'str': str, 'int': int,
                'float': float, 'list': list, 'dict': dict, 'range': range,
                'sum': sum, 'max': max, 'min': min
            }
        }
        
        import io
        import contextlib
        
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(code, safe_globals)
        
        result = output.getvalue()
        return result if result else "Code executed successfully (no output)"
        
    except Exception as e:
        return f"Python execution error: {str(e)}"
