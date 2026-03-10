<p align="center">
  <img src="https://raw.githubusercontent.com/slpuk/lightcorn/refs/heads/main/images/logo.png" alt="Lightcorn logo" width="400"/>
</p>

> A lightweight ASGI server for Python with zero dependencies

![Protocol Version](https://img.shields.io/badge/version-0.3.0-blue?style=for-the-badge)
![Development Status](https://img.shields.io/badge/status-alpha-red?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.7+-blue?style=for-the-badge&logo=python&logoColor=white)

## About
**Lightcorn** is a minimalist ASGI server written in pure Python, built entirely on the standard library. It's designed for developers who want to understand how ASGI servers work under the hood, or need a lightweight server for simple applications.

## Project Structure
```text
lightcorn
├── lightcorn/
│   ├── __init__.py     # Package exports and metadata
│   └─── server.py      # Core server implementation
├── LICENSE             # MIT license
├── pyproject.toml      # PIP config
└── README.md           # This file
```

## License
This project is licensed under the [MIT License](https://github.com/slpuk/lightcorn/blob/main/LICENSE).

## Disclaimer
Lightcorn is currently in alpha development.
It's great for learning and experimentation, but not yet recommended for production use!
