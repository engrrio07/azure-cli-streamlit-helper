import streamlit as st
import subprocess
import json

st.set_page_config(page_title="Azure CLI Helper", layout="wide")
st.title("Azure CLI Helper (Using Current az login Context)")

st.info("This app uses your existing Azure CLI login session. Please run `az login` in your terminal before using this app.")

def run_az_command(cmd):
    """Run an Azure CLI command and return output or error."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return str(e)

# Option selection
option = st.selectbox(
    "Choose an action:",
    [
        "Find Service Principal ID by Name",
        "Find Service Principal Name by ID",
        "Show Current Azure Account"
    ]
)

if option == "Find Service Principal ID by Name":
    sp_name = st.text_input("Enter Service Principal Name:")
    if st.button("Search by Name") and sp_name:
        cmd = f'az ad sp list --display-name "{sp_name}" --query "[].{{id:appId, name:displayName}}" -o json'
        output = run_az_command(cmd)
        try:
            data = json.loads(output)
            st.json(data)
        except Exception:
            st.code(output)

if option == "Find Service Principal Name by ID":
    sp_id = st.text_input("Enter Service Principal ID:")
    if st.button("Search by ID") and sp_id:
        cmd = f'az ad sp show --id "{sp_id}" --query "{{appId:appId, displayName:displayName}}" -o json'
        output = run_az_command(cmd)
        try:
            data = json.loads(output)
            st.json(data)
        except Exception:
            st.code(output)

if option == "Show Current Azure Account":
    if st.button("Show Account Info"):
        cmd = "az account show -o json"
        output = run_az_command(cmd)
        try:
            data = json.loads(output)
            st.json(data)
        except Exception:
            st.code(output)

st.caption("Make sure you are logged in with `az login` before using this app.")
