🧠 HackYeah 2025 – Smart Civic Opportunities Backend

This repository contains the backend service for our HackYeah 2025 project, a platform that connects citizens with local civic engagement opportunities — from environmental projects to cultural initiatives — using semantic search powered by Google Gemini embeddings and ChromaDB vector storage.

The backend is built with Flask and implements secure, scalable APIs for adding and querying opportunities (so-called ogłoszenia), with strong data validation, geocoding, and AI-driven search.

🚀 Features

🔒 Secure API with API key authentication and rate limiting

🧭 Geolocation-aware – automatically resolves coordinates to city names using OpenStreetMap

🧠 Semantic search – natural language matching of opportunities via Google Gemini embeddings and ChromaDB

✅ Validation layer – enforces domain-specific constraints (allowed tags, workloads, forms)

🌍 REST API design – two core endpoints for data insertion and querying

⚙️ Production-safe Flask setup – with security headers, request limiting, and UTF-8 support

🧩 Tech Stack
Component	Technology
Web Framework	Flask
Database	Chroma CloudDB
Embedding Model	Google Gemini (gemini-embedding-001)
Rate Limiting	Flask-Limiter
Environment Management	python-dotenv
Reverse Geocoding	OpenStreetMap (Nominatim API)
Hosting	Any cloud/VM (DigitalOcean, GCP, etc.)
