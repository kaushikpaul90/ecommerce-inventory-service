# Inventory Service

A microservice for managing inventory in an e-commerce system, built with FastAPI and Python.

## Overview

The Inventory Service is part of a microservices-based e-commerce system. It handles:
- Stock management
- Inventory reservations for orders
- Stock level queries
- Inventory updates

## Features

- RESTful API endpoints for inventory management
- Real-time stock level tracking
- Order reservation system
- Health check endpoint
- Database service integration
- Containerized deployment support
- Kubernetes deployment via Helm charts

## Tech Stack

- Python 3.11
- FastAPI
- Pydantic for data validation
- HTTPX for async HTTP requests
- Uvicorn ASGI server
- Docker for containerization
- Kubernetes (via Helm) for orchestration

## Prerequisites

- Python 3.11 or higher
- Docker (for containerized deployment)
- Kubernetes cluster (for production deployment)
- Helm (for Kubernetes deployment)

## Installation

### Local Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the service:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8006 --reload
   ```

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t inventory-service .
   ```

2. Run the container:
   ```bash
   docker run -d -p 8006:8006 inventory-service
   ```

### Kubernetes Deployment (using Helm)

1. Navigate to the helm chart directory:
   ```bash
   cd helm_chart
   ```

2. Install the chart:
   ```bash
   helm install inventory-service .
   ```

## API Endpoints

- `GET /health` - Health check endpoint
- `POST /admin/seed` - Seed sample inventory data
- `POST /reserve` - Reserve inventory for an order
- More endpoints documented in the FastAPI Swagger UI

## Configuration

The service can be configured using environment variables:

- `DATABASE_SERVICE_URL` - URL of the database service (default: "http://192.168.105.2:30000")
- Additional configuration can be set via the Helm values.yaml file for Kubernetes deployment

## Documentation

API documentation is automatically generated and available at:
- Swagger UI: `http://localhost:8006/docs`
- ReDoc: `http://localhost:8006/redoc`

## Development

The service follows standard Python development practices:
- Type hints for better code clarity
- Pydantic models for data validation
- Async/await for efficient I/O operations
- Error handling with proper HTTP status codes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]
This repository contains the source code of Inventory Service of the E-Commerce application
