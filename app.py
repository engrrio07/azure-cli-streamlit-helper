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

option = st.selectbox(
    "Choose an action:",
    [
        "Find Service Principal ID by Name",
        "Find Service Principal Name by ID",
        "Show Current Azure Account",
        "List all Service Principals",
        "Show Service Principal Details",
        "Create a Service Principal",
        "Check Management Group Name Availability",
        "Create Management Group",
        # "Delete Management Group",  # Removed for safety
        "List Management Groups",
        "Show Management Group Details",
        "Update Management Group",
        "List Subscriptions"
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

if option == "List all Service Principals":
    if st.button("List Service Principals"):
        cmd = "az ad sp list --all -o json"
        output = run_az_command(cmd)
        try:
            data = json.loads(output)
            st.json(data)
        except Exception:
            st.code(output)

if option == "Show Service Principal Details":
    sp_id = st.text_input("Enter Service Principal ID or Object ID:")
    if st.button("Show Details") and sp_id:
        cmd = f'az ad sp show --id "{sp_id}" -o json'
        output = run_az_command(cmd)
        try:
            data = json.loads(output)
            st.json(data)
        except Exception:
            st.code(output)

if option == "Create a Service Principal":
    sp_name = st.text_input("Enter New Service Principal Name:")
    if st.button("Create Service Principal") and sp_name:
        cmd = f'az ad sp create-for-rbac --name "{sp_name}" -o json'
        output = run_az_command(cmd)
        try:
            data = json.loads(output)
            st.json(data)
        except Exception:
            st.code(output)

if option == "Check Management Group Name Availability":
    mg_name = st.text_input("Enter Management Group Name to Check:")
    if st.button("Check Availability") and mg_name:
        cmd = f'az account management-group check-name-availability --name "{mg_name}" -o json'
        output = run_az_command(cmd)
        try:
            data = json.loads(output)
            st.json(data)
        except Exception:
            st.code(output)

if option == "Create Management Group":
    mg_name = st.text_input("Enter New Management Group Name:")
    mg_display_name = st.text_input("Enter Display Name (optional):")
    if st.button("Create Management Group") and mg_name:
        cmd = f'az account management-group create --name "{mg_name}"'
        if mg_display_name:
            cmd += f' --display-name "{mg_display_name}"'
        cmd += ' -o json'
        output = run_az_command(cmd)
        try:
            data = json.loads(output)
            st.json(data)
        except Exception:
            st.code(output)

if option == "List Management Groups":
    if st.button("List Management Groups"):
        cmd = "az account management-group list -o json"
        output = run_az_command(cmd)
        try:
            data = json.loads(output)
            st.json(data)
        except Exception:
            st.code(output)

if option == "Show Management Group Details":
    mg_name = st.text_input("Enter Management Group Name:")
    if st.button("Show Details") and mg_name:
        cmd = f'az account management-group show --name "{mg_name}" -o json'
        output = run_az_command(cmd)
        try:
            data = json.loads(output)
            st.json(data)
        except Exception:
            st.code(output)

if option == "Update Management Group":
    mg_name = st.text_input("Enter Management Group Name to Update:")
    mg_display_name = st.text_input("Enter New Display Name (optional):")
    if st.button("Update Management Group") and mg_name:
        cmd = f'az account management-group update --name "{mg_name}"'
        if mg_display_name:
            cmd += f' --display-name "{mg_display_name}"'
        cmd += ' -o json'
        output = run_az_command(cmd)
        try:
            data = json.loads(output)
            st.json(data)
        except Exception:
            st.code(output)

if option == "List Subscriptions":
    if st.button("List Subscriptions"):
        cmd = "az account list -o json"
        output = run_az_command(cmd)
        try:
            data = json.loads(output)
            st.json(data)
        except Exception:
            st.code(output)

st.caption("Make sure you are logged in with `az login` before using this app.")
