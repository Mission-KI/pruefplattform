# Build versions
ARG UV_REPO_DIGEST=sha256:414111d90a661726e63d82f72975bc73eb2943c5f8b2b8da0237a51df5654102
ARG PYTHON_REPO_DIGEST=sha256:e52ca5f579cc58fed41efcbb55a0ed5dccf6c7a156cba76acfb4ab42fc19dd00
ARG TINI_VERSION=0.19.0-1

# Setting unix timestamps to today 18.03.2025
ARG SOURCE_DATE_EPOCH=1742214363

ARG UID=12407

# Build stage for building the python environment
FROM ghcr.io/astral-sh/uv@${UV_REPO_DIGEST} AS builder

# Source Date Epoch
ARG SOURCE_DATE_EPOCH UID
ENV SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH}

# Install tini
ARG TINI_VERSION
SHELL ["/bin/bash", "-c"]
RUN set -xEeu && \
    export DEBIAN_FRONTEND="noninteractive" && \
	apt-get update && \
	apt-get install -y --no-install-recommends \
        tini=${TINI_VERSION} && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/log/*

# UV environment variables
# UV_COMPILE_BYTECODE=0: Don't pre-compile __pycache__, in some cases these are sensitive to timestamps and the build becomes not reproducible
# UV_NO_INSTALLER_METADATA=1: Prevents metadata like the "uv_cache.json" to be created, which includes timestamps
# UV_PYTHON_DOWNLOADS=0: Use the pre-installed python interpreter
ENV UV_COMPILE_BYTECODE=0 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0 UV_NO_INSTALLER_METADATA=1

# Run anything with user privileges
RUN useradd -u ${UID} user		
USER user
WORKDIR /home/user
ENV TOOL_WORKDIR=/home/user

# Copy source files
COPY --chown=user:user . /home/user

# Install python dependencies
RUN --mount=type=cache,target=/home/user/.cache/uv,uid=${UID} \
    uv sync --frozen --no-install-project --no-dev --no-cache



# Install project
RUN --mount=type=cache,target=/home/user/.cache/uv,uid=${UID} \
    uv sync --frozen --no-dev --no-cache

# Use a final python image without uv
FROM python@${PYTHON_REPO_DIGEST}

# Source Date Epoch
ARG SOURCE_DATE_EPOCH UID
ENV SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH}

# Copy the tini from the builder
COPY --from=builder /usr/bin/tini /usr/bin/tini

# Run anything with user privileges
RUN useradd -u ${UID} user		
USER user
WORKDIR /home/user

# Copy the application from the builder
COPY --from=builder --chown=user:user /home/user /home/user

# Place executables in the environment at the front of the path
ENV PATH="/home/user/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=True

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD [ "python","-u","src/enpkg/main.py" ]