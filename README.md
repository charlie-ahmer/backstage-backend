# Backstage Backend

Backend and data ingestion system for a music-focused platform. This project handles intake data from a WordPress website, stores it in PostgreSQL, and supports future expansion for subscriptions, band features, and additional product workflows.

## Overview

This backend was built to support a website with multiple intake sources:

- Newsletter signups
- Band application form
- Band list research data from Google Sheets

Form submissions are sent from WordPress to a FastAPI backend, which validates and inserts the data into a PostgreSQL database hosted on Neon. A separate Python sync process is used to bring Google Sheets data into the database.

## Architecture

### Frontend / intake layer
- **WordPress** with Astra theme for marketing pages
- **Elementor** for page building
- **Fluent Forms Pro** for:
  - Newsletter signup form
  - Band application form

Each form is configured with a webhook that sends JSON payloads to the backend API using Bearer token authentication.

### Backend
- **FastAPI**
- Endpoints such as:
  - `POST /api/intake/newsletter`
  - `POST /api/intake/band-application`
- Token-protected API access
- Database inserts using PostgreSQL connection logic

### Database
- **Neon PostgreSQL**
- Stores operational and future-facing tables such as:
  - `newsletter_signups`
  - `customers`
  - `subscriptions`
  - `bands`
  - `band_applications`
  - `band_research`

### Data sync / ETL
- Python script used to ingest Google Sheets / CSV-based band list data into Postgres

### Deployment
- **Railway** for containerized backend hosting
- **GitHub** for source control and deployment workflow

---

## Tech Stack

- Python
- FastAPI
- PostgreSQL / Neon
- Railway
- WordPress
- Elementor
- Fluent Forms Pro
- GitHub

## Features

- Accepts newsletter signup submissions from website forms
- Accepts band application submissions from website forms
- Stores intake data in PostgreSQL
- Supports token-authenticated API ingestion
- Syncs external research/list data into database
- Structured for future growth into subscriptions and additional product workflows

## Example Data Flow

1. User submits a form on the WordPress site
2. Fluent Forms sends a JSON webhook request to FastAPI
3. FastAPI validates the request and auth token
4. Backend writes the submission into Neon PostgreSQL
5. Additional scripts sync external structured data into related tables

## Project Goals

- Centralize intake data from multiple sources
- Create a clean operational database for future product use
- Reduce manual data handling
- Build a scalable backend foundation for a potential business

## Future Improvements

- Add stronger authentication and role-based access
- Add request logging and monitoring
- Add validation layers with Pydantic models
- Add automated scheduled syncs for external data sources
- Add analytics-ready modeled tables
- Add tests for API endpoints and database operations
- Add admin/reporting interface

