# BPMN-CPI Example
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)

This repository implements a full simulation of a manufacturing system using BPMN+CPI. It enables the evaluation of strategies across multiple KPIs such as revenue, timing, and resource usage. Using AALpy, we extract a Markov Decision Process (MDP) to analyze outcomes probabilistically.

## Prerequisites

- **Python 3.12+**

    To install **Python**, follow the instructions on [Python's official website](https://www.python.org/downloads/). 

---
## Quick Start

### Using Python
To start the application using Python, follow these steps:
1. **Environment Setup**
- **Using Conda**
    ```bash
    conda create --name bpmn-cpi python=3.12
    conda activate bpmn-cpi
    ```
- **Using venv**
    ```bash
    python3.12 -m venv bpmn-cpi
    source bpmn-cpi/bin/activate  # On macOS/Linux
    bpmn-cpi\Scripts\activate     # On Windows
    ```

2. **Install required dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Running the `main.ipynb` Notebook**
   To start the `main.ipynb` notebook directly, use the following command:
    ```bash
    jupyter notebook main.ipynb --port=8888
    ```
   Open a browser and go to `http://127.0.0.1:8888` to access the Jupyter environment and run the `main.ipynb` notebook.

---