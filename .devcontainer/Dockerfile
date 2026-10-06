FROM debian:bookworm-slim

# ── Pinned versions ───────────────────────────────────────────────────────────
# This is the single place to update tool versions.
# To upgrade a tool: change the value and rebuild.
ARG ENTIRE_VERSION="0.8.0"
ARG UV_VERSION="0.12.22"
# ─────────────────────────────────────────────────────────────────────────────

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        git \
        curl \
        ca-certificates \
        unzip \
        python3 \
        python3-venv \
        locales && \
    sed -i 's/^# *en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen && \
    locale-gen && \
    rm -rf /var/lib/apt/lists/*

# Node.js LTS (required for Claude Code)
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        -o /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        > /etc/apt/sources.list.d/github-cli.list && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends gh && \
    rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    TZ=Europe/Amsterdam

# Non-root user
ARG USERNAME=dev
ARG UID=1000
ARG GID=1000

RUN groupadd --gid ${GID} ${USERNAME} && \
    useradd --uid ${UID} --gid ${GID} -m -s /bin/bash ${USERNAME} && \
    mkdir -p /workspace && chown ${USERNAME}:${USERNAME} /workspace

# Install entireio/cli
RUN set -eux; \
    curl -Lo /tmp/entire.tar.gz \
        "https://github.com/entireio/cli/releases/download/v${ENTIRE_VERSION}/entire_linux_amd64.tar.gz"; \
    tar -C /tmp -xzf /tmp/entire.tar.gz entire; \
    mv /tmp/entire /usr/local/bin/entire; \
    rm /tmp/entire.tar.gz; \
    entire --version

# Install uv
RUN curl -LsSf "https://astral.sh/uv/${UV_VERSION}/install.sh" | \
        env UV_INSTALL_DIR=/usr/local/bin UV_NO_MODIFY_PATH=1 sh && \
    uv --version

COPY onboard.sh /usr/local/bin/dair-onboard
RUN chmod 755 /usr/local/bin/dair-onboard

WORKDIR /workspace
USER ${USERNAME}

ENV PATH="/home/${USERNAME}/.local/bin:/usr/local/bin:/usr/bin:/sbin:/bin"

# Claude / Anthropic Foundry
ENV CLAUDE_CODE_USE_FOUNDRY=1 \
    ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-5-5 \
    ANTHROPIC_DEFAULT_SONNET_MODEL=claude-sonnet-5-5 \
    ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-haiku-4-5

# Install Claude Code CLI
RUN curl -fsSL https://claude.ai/install.sh | bash

RUN echo '[[ $- == *i* ]] && { dair-onboard --if-needed || true; }' >> ~/.bashrc

CMD ["bash"]
