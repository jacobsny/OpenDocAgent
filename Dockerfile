FROM python:3.11-slim

# Install system dependencies for pandoc, texlive, and nodejs (for mermaid)
RUN apt-get update && apt-get install -y \
    pandoc \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-extra-utils \
    texlive-latex-extra \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install mermaid-cli globally
RUN npm install -g @mermaid-js/mermaid-cli

# Set working directory
WORKDIR /app

# Copy python project
COPY pyproject.toml README.md ./
COPY opendocagent ./opendocagent

# Install dependencies
RUN pip install --no-cache-dir .

ENTRYPOINT ["opendoc"]
