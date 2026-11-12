@echo off
rem Plain Claude for brainstorming and questions: no files, no shell, no GitHub.
rem This file just calls "TEMU Claude Agent (GitHub).bat" in chat mode.
rem Model: claude-opus-5-5 (best), claude-sonnet-5-5 (half price), claude-haiku-5-5 (cheapest)
set "MODEL=claude-opus-5-5"
set "CHAT=1"
call "%~dp0TEMU Claude Agent (GitHub).bat"
