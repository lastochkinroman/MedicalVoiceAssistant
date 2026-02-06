"""Test script to debug module imports."""
import sys
print('Python version:', sys.version)
print('Version info:', sys.version_info)

print('\n--- Testing imports ---')
try:
    import config
    print('✓ config module imported')
except Exception as e:
    print(f'✗ config module failed: {type(e).__name__}: {e}')
    import traceback
    print(f'Stack trace:\n{traceback.format_exc()}')

print('\n--- Testing audio_processor ---')
try:
    import audio_processor
    print('✓ audio_processor module imported')
except Exception as e:
    print(f'✗ audio_processor module failed: {type(e).__name__}: {e}')
    import traceback
    print(f'Stack trace:\n{traceback.format_exc()}')

print('\n--- Testing speech_recognizer ---')
try:
    import speech_recognizer
    print('✓ speech_recognizer module imported')
except Exception as e:
    print(f'✗ speech_recognizer module failed: {type(e).__name__}: {e}')
    import traceback
    print(f'Stack trace:\n{traceback.format_exc()}')

print('\n--- Testing medical_analyzer ---')
try:
    import medical_analyzer
    print('✓ medical_analyzer module imported')
except Exception as e:
    print(f'✗ medical_analyzer module failed: {type(e).__name__}: {e}')
    import traceback
    print(f'Stack trace:\n{traceback.format_exc()}')

print('\n--- Testing main ---')
try:
    import main
    print('✓ main module imported')
except Exception as e:
    print(f'✗ main module failed: {type(e).__name__}: {e}')
    import traceback
    print(f'Stack trace:\n{traceback.format_exc()}')