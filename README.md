# AI Interviewer

AI-powered personalized voice interview platform.

## Overview

The system creates personalized technical interviews using:

- Candidate Resume
- Job Description
- Optional GitHub profile
- Optional recruiter instructions

The AI generates interview questions dynamically, evaluates candidate answers, and produces a final interview score and report.

## Architecture

Frontend:
React + Vite

Backend:
FastAPI + Python

AI:
Groq LLM + Whisper

Database:
PostgreSQL

Deployment:
Vercel + Render

Optional:
GitHub API
Qdrant
LangChain / LangGraph
n8n

## Project Structure

```text
ai-interviewer/
├── backend/
├── frontend/
├── README.md
├── LICENSE
└── .gitignore