FROM python:3.12-slim

WORKDIR /app

# Install system dependencies if any
# RUN apt-get update && apt-get install -y ...

# Install uv
RUN pip install uv

# Copy dependencies first for caching
COPY pyproject.toml .
COPY uv.lock .

# Create venv and install dependencies
RUN uv venv .venv
RUN uv pip install -r pyproject.toml --python .venv
# Just in case pyproject.toml install fails or we need editable install of src
# We will copy source later, but let's install the dependencies explicitly
RUN uv sync --python .venv

# Copy source code
COPY src/ src/
COPY .streamlit/ .streamlit/
# COPY data/ data/ # We will mount this using volume

# Expose Streamlit port
EXPOSE 8501

# Run the application
CMD [".venv/bin/streamlit", "run", "src/app.py"]
