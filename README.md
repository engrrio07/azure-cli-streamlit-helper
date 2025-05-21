# Azure CLI Helper (Streamlit App)

A simple Streamlit app to streamline common Azure CLI commands, such as finding service principal IDs or names, using your current `az login` context.

## Features

- **Find Service Principal ID by Name**
- **Find Service Principal Name by ID**
- **Show Current Azure Account Info**
- **List Subscriptions**
- **Show Service Principal Details**
- **List ACE Groups and Members in Entra**
- **List API Managed Identities**
- **Check DSMC Rules**
- **No extra authentication required** (uses the credentials from your current `az login` session)
- **Streamlit telemetry disabled** for privacy

## Prerequisites

- Python 3.8+
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed and authenticated (`az login`)
- Docker (optional, for containerized deployment)

## Local Usage

1. Clone this repo and navigate into it.
2. Install Python dependencies:
    ```
    pip install -r requirements.txt
    ```
3. Run the app:
    ```
    streamlit run app.py
    ```
4. Open [http://localhost:8501](http://localhost:8501) in your browser.

## Docker Usage

1. Build the Docker image:
    ```
    docker build -t azure-cli-helper .
    ```
2. Run the container (mount your Azure CLI config for authentication):
    ```
    docker run -it -p 8501:8501 -v ~/.azure:/root/.azure azure-cli-helper
    ```
3. Open [http://localhost:8501](http://localhost:8501) in your browser.

## Notes

- **Authentication:** The app uses your existing Azure CLI login session. Make sure you run `az login` before starting the app (or mount your `.azure` config in Docker).
- **Security:** Do not expose this app to the public internet unless you understand the security implications.

## License

MIT
