# Web UI Target Project
A simple web application built with Flask that provides various UI elements and interactions for testing purposes. This application is designed to help QA engineers and developers practice their web UI automation testing skills.

This project is part of the learning materials for web UI testing and serves as a practical playground for implementing test automation frameworks.
## Overview
This project provides a web-based user interface testing target application. It serves as a controlled environment for practicing web UI automation testing.

## Features
- Multiple UI elements for testing interactions
- Form submissions and validations
- Dynamic content loading from previously ctored `CSV` file
- Basic authentication flows

## Getting Started

### Prerequisites
- `Python 3.9` or higher
- `pip` or `uv` package manager

### Installation
1. Clone the repository
```bash
git clone https://github.com/yourusername/web_ui_target.git
cd web_ui_target
```

2. Create and activate virtual environment (optional but recommended)
```bash
python -m venv .venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```
or
```bash
uv pip install -e .
```

4. Run tests
```bash
pytest app.py
```
or 
```bash
uv run app.py
```

## Usage
The application will be available at `http://localhost:5000` by default.
