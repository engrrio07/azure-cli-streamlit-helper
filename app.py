import streamlit as st
import subprocess
import json

st.set_page_config(page_title="Azure CLI Helper", layout="wide")
st.title("Azure CLI Helper (Using Current az login Context)")

st.info("This app uses your existing Azure CLI login session. Please run `az login` in your terminal before using this app.")

# Fetch the current subscription
original_subscription = subprocess.run(
    "az account show --query 'id' --output tsv", shell=True, capture_output=True, text=True
).stdout.strip()

def run_az_command(cmd, jsonLoad=True):
    """Run an Azure CLI command and return output or error, then revert to original subscription."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            output = json.loads(result.stdout) if jsonLoad else result.stdout

            # Revert to original subscription after execution
            subprocess.run(f'az account set --subscription "{original_subscription}"', shell=True)

            return output
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return str(e)

def check_dsmc_rules(selected_subscriptions, dsmc):
    """Check DSMC rules in Network Security Groups across subscriptions."""
    results = []

    for subscription in selected_subscriptions:
        run_az_command(f'az account set --subscription "{subscription}"')
        nsg_output = run_az_command('az network nsg list --query "[].name" --output json')

        try:
            network_security_groups = nsg_output
        except json.JSONDecodeError:
            st.error(f"Failed to parse NSG list for subscription {subscription}")
            continue

        if not network_security_groups:
            continue

        for network_security_group in network_security_groups:
            resource_group_cmd = f'az network nsg list --query "[?name==\'{network_security_group}\'].resourceGroup" --output json'
            resource_group_output = run_az_command(resource_group_cmd)

            try:
                resource_group = resource_group_output
                resource_group = resource_group[0] if resource_group else None  # Extract single value
            except json.JSONDecodeError:
                st.error(f"Failed to parse Resource Group for NSG {network_security_group}")
                continue

            if not resource_group:
                continue

            dsmc_rules_cmd = f'az network nsg rule list --resource-group "{resource_group}" --nsg-name "{network_security_group}" --query "[?contains(name,\'ipv4\') && starts_with(name,\'{dsmc}\')]" --output json'
            dsmc_rule_found = run_az_command(dsmc_rules_cmd)

            try:
                rules_list = dsmc_rule_found
            except json.JSONDecodeError:
                st.error(f"Failed to parse DSMC rules for {network_security_group}")
                continue

            if not rules_list:
                continue  # Skip if no matching rules found

            cmd_rules_table = f'az network nsg rule list --resource-group "{resource_group}" --nsg-name "{network_security_group}" --query "[?contains(name,\'ipv4\') && starts_with(name,\'{dsmc}\')]" --output table'
            rules_table = run_az_command(cmd_rules_table, jsonLoad=False)

            results.append({
                "Subscription": subscription,
                "Network Security Group": network_security_group,
                "Resource Group": resource_group,
                "Rules": rules_table
            })

    return results

option = st.selectbox(
    "Choose an action:",
    [
        "Show Current Azure Account",
        "List Subscriptions",
        "Show Service Principal Details",
        "Find Service Principal ID by Name",
        "Find Service Principal Name by ID",
        "List ACE Groups and Members in Entra",
        "List API Managed Identities",
        "Check DSMC Rules"
    ]
)

if option == "Find Service Principal ID by Name":
    sp_name = st.text_input("Enter Service Principal Name:")
    if st.button("Search by Name") and sp_name:
        cmd = f'az ad sp list --display-name "{sp_name}" --query "[].{{id:id, displayName:displayName}}" -o json'
        output = run_az_command(cmd)
        try:
            data = output
            st.json(data)
        except Exception:
            st.code(output)

if option == "Find Service Principal Name by ID":
    sp_id = st.text_input("Enter Service Principal ID:")
    if st.button("Search by ID") and sp_id:
        cmd = f'az ad sp show --id "{sp_id}" --query "{{id:id, displayName:displayName}}" -o json'
        output = run_az_command(cmd)
        try:
            data = output
            st.json(data)
        except Exception:
            st.code(output)

if option == "Show Current Azure Account":
    if st.button("Show Account Info"):
        cmd = "az account show -o json"
        output = run_az_command(cmd)
        try:
            data = output
            st.json(data)
        except Exception:
            st.code(output)

if option == "Show Service Principal Details":
    sp_id = st.text_input("Enter Service Principal ID or Object ID:")
    if st.button("Show Details") and sp_id:
        cmd = f'az ad sp show --id "{sp_id}" -o json'
        output = run_az_command(cmd)
        try:
            data = output
            st.json(data)
        except Exception:
            st.code(output)

if option == "List Subscriptions":
    if st.button("List Subscriptions"):
        cmd = "az account list -o json"
        output = run_az_command(cmd)
        try:
            data = output
            st.json(data)
        except Exception:
            st.code(output)

if option == "List ACE Groups and Members in Entra":
    ace_team = st.text_input("Enter ACE Team name:")
    if st.button("List Members") and ace_team:
        cmd = f'az ad group list --display-name "{ace_team}" --output tsv --query "[].id" | xargs'
        group_ids_output = run_az_command(cmd, jsonLoad=False)
        group_ids = group_ids_output.split()
        
        results = []
        for group in group_ids:
            group_info_cmd = f'az ad group show --group "{group}" --query "{{displayName:displayName, objectId:id}}" -o json'
            group_info_output = run_az_command(group_info_cmd)
            try:
                group_info = group_info_output
            except json.JSONDecodeError:
                group_info = {"displayName": "Unknown", "objectId": group}

            members_cmd = f'az ad group member list --group "{group}" --query "[].displayName" -o json'
            members_output = run_az_command(members_cmd)
            try:
                members = members_output
            except json.JSONDecodeError:
                members = ["Error retrieving members"]

            group_info["members"] = members
            results.append(group_info)

        st.json(results)

if option == "List API Managed Identities":
    api_name = st.text_input("Enter API name:")
    if st.button("List Managed Identities") and api_name:
        cmd = f'az ad sp list --display-name "umid-{api_name}" --query "[].id" -o json'
        sp_ids_output = run_az_command(cmd)

        try:
            sp_ids = sp_ids_output
        except json.JSONDecodeError:
            st.error("Error retrieving managed identities")
            sp_ids = []

        results = []
        for sp in sp_ids:
            sp_info_cmd = f'az ad sp show --id "{sp}" --query "{{displayName:displayName, objectId:id}}" -o json'
            sp_info_output = run_az_command(sp_info_cmd)
            try:
                sp_info = sp_info_output
            except json.JSONDecodeError:
                sp_info = {"displayName": "Unknown", "objectId": sp}

            subscription_cmd = f'az ad sp show --id "{sp}" --query "alternativeNames[1]" -o json'
            subscription_output = run_az_command(subscription_cmd)
            try:
                subscription_id = subscription_output.split("/")[2]
                subscription_name_cmd = f'az account show --name "{subscription_id}" --query "name" -o json'
                subscription_name_output = run_az_command(subscription_name_cmd)
                subscription_name = subscription_name_output

            except (json.JSONDecodeError, AttributeError):
                subscription_name = "Unknown"

            sp_info["subscription"] = subscription_name
            results.append(sp_info)

        st.json(results)

if option == "Check DSMC Rules":
    # User-defined DSMC variable
    dsmc = st.text_input("Enter DSMC prefix:")

    # Get user-defined keywords
    filter_keywords = st.text_area("Enter subscription pcodes (comma-separated)")

    # Convert input into a list
    keyword_list = filter_keywords.split(",") if filter_keywords else []

    # Build the jq query dynamically
    jq_filter = "|".join(keyword_list) if keyword_list else ".*"  # Match all if empty

    # Run az command with dynamic filtering
    all_subscriptions = run_az_command(f'az account list --output json | jq -r \'[.[].name] | map(select(. | test("{jq_filter}")))\'')

    # Checkbox for selecting all subscriptions
    select_all = st.checkbox("Select All Subscriptions")

    # User selection logic
    selected_subscriptions = all_subscriptions if select_all else st.multiselect("Select Subscriptions", all_subscriptions)

    if st.button("Run DSMC Rules Check") and dsmc and selected_subscriptions:
        rules_data = check_dsmc_rules(selected_subscriptions, dsmc)
        if rules_data:
            st.json(rules_data)
        else:
            st.warning("No matching DSMC rules found.")

st.caption("Make sure you are logged in with `az login` before using this app.")
st.markdown(
    "<div style='text-align: center; font-size: 12px; color: gray;'>© 2025 R.A.</div>",
    unsafe_allow_html=True
)
