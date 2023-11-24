from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.subscription import SubscriptionClient
from azure.storage.blob import ContainerClient


def enumerate_blob_storage(_credentials):
    # Iterate over all the available subscriptions
    subscription_client = SubscriptionClient(_credentials)
    for subscription in subscription_client.subscriptions.list():

        rmc = ResourceManagementClient(_credentials, subscription.subscription_id)
        for rg in rmc.resource_groups.list():
            rg_name = rg.name

            smc = StorageManagementClient(_credentials, subscription.subscription_id)
            for account in smc.storage_accounts.list_by_resource_group(rg_name):
                account_name = account.name

                sub_name = subscription.display_name

                for container in smc.blob_containers.list(account_name=account_name, resource_group_name=rg_name):
                    output = []
                    container_name = container.name

                    url = get_account_url(account_name)
                    cc = ContainerClient(url, container_name, _credentials)
                    properties = cc.get_container_properties()
                    container_last_modified = properties['last_modified']
                    container_public_access = properties['public_access']

                    output += [sub_name, rg_name, account_name, container_name, str(container_last_modified),
                               str(container_public_access)]

                    try:
                        for blob in cc.list_blobs():
                            output += [blob.name, str(blob.last_modified), str(blob.size)]
                    finally:
                        pass

                    csv = ','.join(output)
                    print(csv)


def get_account_url(account_name):
    return "https://" + account_name + ".blob.core.windows.net/"


if __name__ == '__main__':
    credentials = DefaultAzureCredential()
    enumerate_blob_storage(credentials)
