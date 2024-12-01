import uuid
from azure.identity import DefaultAzureCredential
from azure.mgmt.authorization import AuthorizationManagementClient
import requests

# Replace with your actual values
subscription_id = "f12b721a-38e7-4d35-a686-0af70d663353"  # Azure Subscription ID
resource_group_name = "resgroupa7"  # Resource Group Name
assignee_email = "wi22b004@technikum-wien.at"  # Email of the user to assign the role

# Azure Role Definition ID for "Reader"
reader_role_id = "acdd72a7-3385-48ef-bd42-f606fba81ae7"

def get_user_object_id(email: str) -> str:
    """Fetch the Object ID of a user using Microsoft Graph API."""
    credential = DefaultAzureCredential()

    # Obtain an access token for Microsoft Graph
    token = credential.get_token("https://graph.microsoft.com/.default")
    headers = {"Authorization": f"Bearer {token.token}"}

    # Query the Microsoft Graph API
    url = f"https://graph.microsoft.com/v1.0/users?$filter=mail eq '{email}'"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"Error fetching user data: {response.text}")

    data = response.json()
    if "value" not in data or not data["value"]:
        raise RuntimeError(f"User with email '{email}' not found.")
    return data["value"][0]["id"]

def list_available_roles():
    """List all available roles in the subscription."""
    credential = DefaultAzureCredential()
    client = AuthorizationManagementClient(credential, subscription_id)

    print("\nAvailable Roles:")
    roles = client.role_definitions.list(scope=f"/subscriptions/{subscription_id}")
    for role in roles:
        print(f"Role Name: {role.role_name}, Role ID: {role.id}")

def assign_reader_role(object_id: str):
    """Assign the 'Reader' role to the specified user at the resource group scope."""
    credential = DefaultAzureCredential()
    client = AuthorizationManagementClient(credential, subscription_id)

    # Define scope at the resource group level
    resource_group_scope = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"

    # Generate a GUID for the role assignment ID
    role_assignment_id = str(uuid.uuid4())

    # Assign the "Reader" role
    client.role_assignments.create(
        scope=resource_group_scope,
        role_assignment_name=role_assignment_id,
        parameters={
            "properties": {
                "roleDefinitionId": f"/subscriptions/{subscription_id}/providers/Microsoft.Authorization/roleDefinitions/{reader_role_id}",
                "principalId": object_id,
            }
        },
    )
    print(f"Assigned 'Reader' role to user with Object ID '{object_id}'. Role Assignment ID: {role_assignment_id}")

# Main Script
try:
    # Step 1: Get the Object ID of the user
    print("\nFetching user Object ID...")
    user_object_id = get_user_object_id(assignee_email)
    print(f"Object ID for user '{assignee_email}': {user_object_id}")

    # Step 2: List all available roles
    list_available_roles()

    # Step 3: Assign the "Reader" role
    assign_reader_role(user_object_id)

except Exception as e:
    print(f"Error: {e}")
