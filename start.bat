@echo off
echo Starting PPT to Video...
echo Open http://localhost:8765 in your browser
echo Press Ctrl+C to stop
echo.
python -m uvicorn app:app --port 8765
