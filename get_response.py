import base64
import os.path

import requests
import json
import maskpass
from tqdm import tqdm
import time
from concurrent.futures import ThreadPoolExecutor
import configparser


def get_metadata(pod_link, headers, CSP):
    response = requests.get(
        url=f"{pod_link}/cloudview-api/rest/v1/controls/metadata/list?filter=provider%3A{CSP}&pageNo=0&pageSize=1000",
        headers=headers
    )
    # print("status code ", response.status_code, type(response.status_code))
    return response

def get_account_policies(pod_link, headers, CSP):
    response = requests.get(
        url=f"{pod_link}/cloudview-api/rest/v1/reports/policies?cloudType={CSP}",
        headers=headers
    )
    # print("status code ", response.status_code, type(response.status_code))
    return response


def progress_bar(CSP, sleep_time):
    time.sleep(1)
    for i in tqdm(range(100),
                  desc=f"Requesting Data {CSP}",
                  ascii=False, ncols=75):
        time.sleep(sleep_time)

def get_policy_controls(i, pod_link,headers):
    response = requests.get(
        url=f"{pod_link}/cloudview-api/rest/v1/controls/metadata/list?filter=policy.name%3A{i}&pageNo=0&pageSize=100",
        headers=headers
    )
    # print("status code ", response.status_code, type(response.status_code))
    return response


def get_policy(Policies, pod_link, username, password,timestamp):
    auth = f"{username}:{password}"
    b64_auth = base64.b64encode(auth.encode()).decode("utf-8")

    headers = {
        "Authorization": f"Basic {b64_auth}"
    }
    print(Policies)
    response = get_policy_controls(Policies, pod_link, headers)
    # print(resp.json())
    if "errorCode" in dict(response.json()).keys() or "error" in dict(
            response.json()).keys() or response.status_code != 200:
        # print(response.json())
        return response
    else:
        path = "Resposnes"
        if os.path.exists(path):
            with open(f"{path}/{Policies}_{timestamp}.json", "w") as f:
                json.dump(response.json(), f)
        else:
            os.mkdir(path)
            with open(f"{path}/{Policies}_{timestamp}.json", "w") as f:
                json.dump(response.json(), f)
    return response
######################INCOMPLETE#################

def get_policies(csp, pod_link, username, password, timestamp):
    CSP = csp
    auth = f"{username}:{password}"
    b64_auth = base64.b64encode(auth.encode()).decode("utf-8")

    headers = {
        "Authorization": f"Basic {b64_auth}"
    }
    system_defined_policies = {
        "AZURE": [
            "Azure Best Practices Policy",
            "Azure Database Service Best Practices Policy",
            "CIS Microsoft Azure Foundations Benchmark",
            "Azure Function App Best Practices Policy",
            "Azure Infrastructure as Code Security Best Practices Policy"
        ],
        "AWS": [
            "AWS Database Service Best Practices",
            "AWS Best Practices Policy",
            "AWS Lambda Best Practices Policy",
            "CIS Amazon Web Services Foundations Benchmark",
            "AWS Infrastructure as Code Security Best Practices Policy"
        ],
        "GCP" : [
            "GCP Cloud Functions Best Practices Policy",
            "GCP Infrastructure as Code Security Best Practices Policy",
            "GCP Best Practices Policy",
            "GCP Kubernetes Engine Best Practices Policy",
            "GCP Cloud SQL Best Practices Policy",
            "CIS Google Cloud Platform Foundation Benchmark"
        ]

    }
    with ThreadPoolExecutor() as executor:
        progress = executor.submit(progress_bar, CSP, 0.01)
        response = executor.submit(get_account_policies, pod_link, headers, CSP)
        progress.result()
        print("Processing Response...")
        response = response.result()
    if isinstance(response.json(), dict):
        if "errorCode" in dict(response.json()).keys() or "error" in dict(response.json()).keys() or response.status_code != 200:
            return response.json(), response.status_code
    elif response.status_code == 200:
        custom_policies = []
        for i in response.json():
            if i['title'] not in system_defined_policies[CSP]:
                custom_policies.append(i['title'])
        return {"System_Defined": system_defined_policies[CSP], "Custom_Policies": custom_policies}, response.status_code


def call_metadata(csp, pod_link, username, password, timestamp):

    CSP = csp
    auth = f"{username}:{password}"
    b64_auth = base64.b64encode(auth.encode()).decode("utf-8")

    headers = {
        "Authorization": f"Basic {b64_auth}"
    }
    with ThreadPoolExecutor() as executor:
        progress = executor.submit(progress_bar, CSP, 0.01)
        response = executor.submit(get_metadata, pod_link, headers, CSP)
        progress.result()
        print("Processing Response...")
        response = response.result()

    if "errorCode" in dict(response.json()).keys() or "error" in dict(response.json()).keys() or response.status_code != 200:
        # print(response.json())
        return response.json()
    else:
        path = "Resposnes"
        if os.path.exists(path):
            with open(f"{path}/{CSP}_response_{timestamp}.json", "w") as f:
                json.dump(response.json(), f)
        else:
            os.mkdir(path)
            with open(f"{path}/{CSP}_response_{timestamp}.json", "w") as f:
                json.dump(response.json(), f)

# call_metadata("GCP", "https://qualysguard.qg2.apps.qualys.com")
