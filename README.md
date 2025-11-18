# Vegan Agentic Chef 🌱🤖

A simple Streamlit-powered AI agent that suggests easy vegan recipes based on your prompts.

## Overview

Vegan Agentic Chef is a straightforward AI assistant built with Streamlit that helps you discover delicious vegan recipes. Simply describe what you're in the mood for or what ingredients you have, and the agent will suggest easy-to-follow vegan recipes.

## Features

- **Prompt-based Recipe Discovery**: Get recipe suggestions from simple text prompts
- **AI-Powered Recommendations**: Leverages AI to understand your cooking needs
- **Easy-to-Use Interface**: Simple Streamlit web interface
- **Vegan Focus**: All suggestions are 100% plant-based

## Getting Started

### Prerequisites

- Python 3.12 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/czapol/vegan-agentic-chef.git
cd vegan-agentic-chef

# Create and activate virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.streamlit/secrets.toml` file for your API keys and secrets:

```toml
# .streamlit/secrets.toml (not tracked in git)
ANTHROPIC_API_KEY = "your-api-key-here"
# Add other secrets as needed
```

**Note**: The `.streamlit/secrets.toml` file is not committed to the repository for security reasons.

### Running the Application

```bash
# Run the main Streamlit app
streamlit run veganchef.py

# Or run the HTML version
streamlit run veganchefhtml.py
```

The app will open in your default web browser at `http://localhost:8501`.

## Usage

1. Launch the application using one of the commands above
2. Enter a prompt describing what you'd like to cook (e.g., "quick dinner with chickpeas" or "comfort food for cold weather")
3. The AI agent will suggest easy vegan recipes based on your input
4. Follow the recipe suggestions and enjoy your meal!

## Project Structure

```
vegan-agentic-chef/
├── veganchef.py          # Main Streamlit application
├── veganchefhtml.py      # HTML version of the application
├── requirements.txt      # Python dependencies
├── .streamlit/
│   └── secrets.toml     # API keys and secrets (not committed)
└── README.md            # This file
```

**Note**: Only `veganchef*` files are tracked in the repository.

## Tech Stack

- **Framework**: Streamlit
- **Language**: Python 3.12
- **AI**: Anthropic Claude (or other AI provider)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source. Please check the repository for license details.

## Support

For questions or issues, please open an issue on the GitHub repository.

---

Made with 💚 for easy vegan cooking
