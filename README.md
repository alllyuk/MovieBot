# MovieBot

> AI-assisted movie recommendation bot

## Description

[TODO: Add project description after BDD scenarios]

## Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/MovieBot.git
cd MovieBot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
python src/main.py
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src
```

## Project Structure

```
MovieBot/
├── README.md           # This file
├── CLAUDE.md           # AI collaboration notes
├── requirements.txt    # Dependencies
├── src/                # Application code
├── tests/
│   ├── features/       # BDD .feature files
│   └── steps/          # Step definitions
└── .gitignore
```

## License

MIT
