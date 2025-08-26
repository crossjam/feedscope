# Feedscope

A command-line interface (CLI) tool for exploring and managing RSS feed content through the Feedbin API.

## Overview

Feedscope is a Python CLI application that provides convenient access to your Feedbin account, allowing you to manage RSS feed subscriptions, entries, and other content directly from the command line. Built with modern Python tools and designed for developers and power users who prefer terminal-based workflows.

## Goals and Aims

- **Streamlined Feed Management**: Provide quick access to Feedbin's powerful RSS aggregation features without leaving the terminal
- **Developer-Friendly**: Built with type safety, proper error handling, and extensible architecture
- **Secure Authentication**: Safe credential storage with user-specific configuration management
- **API Exploration**: Enable easy exploration and interaction with the full Feedbin API v2 feature set

## Installation

Install using uv (recommended) or pip:

```bash
# Using uv
uv add feedscope

# Using pip
pip install feedscope
```

## Available Commands

### Authentication (`feedscope auth`)

Manage your Feedbin account credentials:

- **`feedscope auth login <email>`** - Authenticate with your Feedbin account
  - Prompts securely for password
  - Validates credentials against Feedbin API
  - Saves credentials to local configuration file
  - Example: `feedscope auth login user@example.com`

- **`feedscope auth remove`** - Remove stored authentication credentials
  - Clears saved login information from configuration
  - Useful for switching accounts or security cleanup

### Configuration

Feedscope automatically manages configuration in your system's user config directory:
- **Location**: `~/.config/dev.pirateninja.feedscope/config.toml` (Linux/macOS)
- **Format**: TOML with secure credential storage
- **Environment Variables**: Override settings with `FEEDSCOPE_*` prefixed variables

## Future Development

This CLI is designed to support the full Feedbin API v2 feature set, including:

- Subscription management (add, remove, organize feeds)
- Entry browsing and filtering
- Unread and starred entry management
- Tag and search functionality
- Import/export capabilities
- Feed icon and metadata access

See [README_ORIGINAL.md](README_ORIGINAL.md) for complete Feedbin API documentation.

## Development

Built with modern Python tools:
- **Python 3.11+** with type hints
- **Typer** for CLI interface and command structure
- **Pydantic** for configuration and data validation
- **HTTPX** for HTTP client functionality
- **Rich** for enhanced terminal output

## Getting Started

1. Install feedscope
2. Authenticate with your Feedbin account:
   ```bash
   feedscope auth login your-email@example.com
   ```
3. Start exploring your feeds (additional commands coming soon!)

For questions or contributions, see the project repository.
