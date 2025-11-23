# 🛠️ Local Development Environment

This guide explains how to run the `mvp-test` and `level-test` applications locally for development and testing.

## Prerequisites

- Python 3 installed on your system.

## Quick Start

1.  Open a terminal in the project root (`math-map-project`).
2.  Run the following command:

    ```bash
    python3 run_local.py
    ```

3.  Access the applications in your browser:

    -   **MVP Test (No Auth)**: [http://localhost:8011](http://localhost:8011)
    -   **Level Test (Auth)**: [http://localhost:8012](http://localhost:8012)
    -   **MVP Test (No Auth)**: [http://localhost:8011](http://localhost:8011)
    -   **Level Test (Auth)**: [http://localhost:8012](http://localhost:8012)
    -   **Adaptive Test (New)**: [http://localhost:8013](http://localhost:8013)
    -   **Backend API**: [http://localhost:5001](http://localhost:5001)

## Features

-   **Simultaneous Execution**: Both apps run at the same time on different ports.
-   **No Caching**: The server is configured to disable caching, so your changes appear immediately upon refresh.
-   **Simple Shutdown**: Press `Ctrl+C` in the terminal to stop both servers.

## Troubleshooting

-   **Port in Use**: If you see an error about the port being in use, make sure no other process is using port 8001 or 8002. You can change the ports in `run_local.py` if needed.
