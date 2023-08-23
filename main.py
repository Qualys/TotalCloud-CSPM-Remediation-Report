import get_response
import consolidated_convert
import separate_convert
import configparser
import datetime
import maskpass

def select_convert_type(CSP, timestamp):
    while True:
        convert_type = input(
            "\nSelect HTML you want\n1 : Separate HTML for control\n2 : Consolidated HTML for controls\n")
        if convert_type not in ['1', '2']:
            print("Wrong input, Try Again !")
            continue
        else:
            break
    if int(convert_type) == 1:
        if isinstance(CSP, list):
            for i in CSP:
                separate_convert.convert_to_html(i, timestamp)
        else:
            separate_convert.convert_to_html(CSP, timestamp)
    elif int(convert_type) == 2:
        if isinstance(CSP, list):
            for i in CSP:
                consolidated_convert.convert_to_html(i, timestamp, False, False)
        else:
            consolidated_convert.convert_to_html(CSP, timestamp, False, False)


def check_response_for_error(resp):
    if resp != None:
        print("\nThere was a problem fetching data, please refer below Message and Try Again : ")
        print(resp)
        return True
    else:
        return False


def get_auth(creds_input):
    if creds_input == '1':
        config = configparser.ConfigParser()
        config.read(".config")
        username = config.get('creds', 'username')
        password = config.get('creds', 'password')
    elif creds_input == '2':
        username = input("Enter your User Name : ")
        # password = input("Enter your Password : ")
        password = maskpass.askpass(prompt="Enter your Password : ", mask="*")
    return username, password


def all_controls(CSP, platform, platform_url, timestamp):
    while True:
        creds_input = input("\nGet Creds From :\n1 : Config File\n2 : Enter Manually\n")
        if creds_input not in list(map(str, [1, 2])):
            continue
        else:
            username, password = get_auth(creds_input)
            break

    if isinstance(CSP, list):
        for i in CSP:
            resp = get_response.call_metadata(i, platform_url[platform], username, password, timestamp)
            if check_response_for_error(resp):
                return False
    else:
        resp = get_response.call_metadata(CSP, platform_url[platform], username, password, timestamp)
        if check_response_for_error(resp):
            return False

    select_convert_type(CSP, timestamp)
    return True


def generate_policy_report(CSP, Policies, resp, policy_title, pod_link, username, password, timestamp):
    if policy_title == 0:
        for i in Policies:
            resp = get_response.get_policy(i, pod_link, username, password, timestamp)
            if resp.status_code != 200:
                if check_response_for_error(resp):
                    return False
            consolidated_convert.convert_to_html(CSP, timestamp, i, True)

    elif policy_title == 1:
        for i in resp['System_Defined']:
            resp = get_response.get_policy(i, pod_link, username, password, timestamp)
            if resp.status_code != 200:
                if check_response_for_error(resp):
                    return False
            consolidated_convert.convert_to_html(CSP, timestamp, i, True)
    elif policy_title == 2:
        for i in resp['Custom_Policies']:
            resp = get_response.get_policy(i, pod_link, username, password, timestamp)
            if resp.status_code != 200:
                if check_response_for_error(resp):
                    return False
            consolidated_convert.convert_to_html(CSP, timestamp, i, True)
    return True

def policy_controls(CSP, resp, pod_link, username, password, timestamp, policy_input):
    Policies = resp['System_Defined'] + resp['Custom_Policies']

    if isinstance(policy_input, list):
        for i in policy_input:
            print(i)
            resp = generate_policy_report(CSP, Policies, resp, i, pod_link, username, password, timestamp)
            if not resp:
                return False

    else:
        resp = generate_policy_report(CSP, Policies, resp, int(policy_input), pod_link, username, password, timestamp)
        if not resp:
            return False
    return True

def policy_wise(CSP, platform, platform_url, timestamp):
    while True:
        creds_input = input("\nGet Creds From :\n1 : Config File\n2 : Enter Manually\n")
        if creds_input not in list(map(str, [1, 2])):
            continue
        else:
            username, password = get_auth(creds_input)
            break
    while True:
        wrong_input = False
        policy_input = input(f"\nSelect Policy To get controls for\n0 : All Policies\n1 : System Defined Policies\n2 : Custom Policies\n")
        if " " in policy_input:
            policy_input = list(map(int, policy_input.split(" ")))

        if isinstance(policy_input, list):
            for i in policy_input:
                if i not in list(range(3)):
                    wrong_input = True
                    break
            if wrong_input:
                print("Wrong Inout, Please Try Again : ")
                continue
        else:
            if policy_input not in list(map(str, range(3))):
                continue
        break
    print(policy_input)


    if isinstance(CSP, list):
        for i in CSP:
            print(i)
            resp, status_code = get_response.get_policies(i, platform_url[platform], username, password, timestamp)
            if status_code != 200:
                if check_response_for_error(resp):
                    return False
            policy_controls(i, resp, platform_url[platform], username, password, timestamp, policy_input)
    else:
        resp, status_code = get_response.get_policies(CSP, platform_url[platform], username, password, timestamp)
        if status_code != 200:
            if check_response_for_error(resp):
                return False
        policy_controls(CSP, resp, platform_url[platform], username, password, timestamp, policy_input)
    return True

def main():
    timestamp = int(datetime.datetime.now().timestamp())
    print(timestamp)
    user_input = ""
    while user_input == "yes" or user_input == "":

        while True:
            platforms = ["US1", "US2", "US3", "US4", "EU1", "EU2", "IN", "CA1", "AE1", "UK1", "AU1"]
            platform = input(f"Enter Your Platform {platforms} : ").upper()
            print(platform)
            if platform not in platforms:
                print("Wrong Input, Please enter correct platform.")
                continue
            break

        platform_url = {"US1" : "https://qualysguard.qualys.com",
                        "US2" : "https://qualysguard.qg2.apps.qualys.com",
                        "US3" : "https://qualysguard.qg3.apps.qualys.com",
                        "US4" : "https://qualysguard.qg4.apps.qualys.com",
                        "EU1" : "https://qualysguard.qualys.eu",
                        "EU2" : "https://qualysguard.qg2.apps.qualys.eu",
                        "IN" : "https://qualysguard.qg1.apps.qualys.in",
                        "CA1" : "https://qualysguard.qg1.apps.qualys.ca",
                        "AE1" : "https://qualysguard.qg1.apps.qualys.ae",
                        "UK1" : "https://qualysguard.qg1.apps.qualys.co.uk",
                        "AU" : "https://qualysguard.qg1.apps.qualys.com.au"}

        while True:
            wrong_input = False
            CSPs = ["AWS", "AZURE", "GCP"]
            CSP = input(f"Please Enter Space separated CSPs if multiple\nEnter Your CSP {CSPs} : ").upper()
            if " " in CSP:
                CSP = CSP.split(" ")
            print(CSP)
            if isinstance(CSP, list):
                for i in CSP:
                    if i not in CSPs:
                        print("Wrong Input, Please enter correct CSP.")
                        wrong_input = True
                        break
                if wrong_input:
                    continue
            else:
                if CSP not in CSPs:
                    print("Wrong Input, Please enter correct CSP.")
                    continue
            break

        while True:
            report_for = input("Please Select, Generate Report For : \n1 : All Controls\n2 : Policy Wise\n")
            if report_for not in list(map(str, [1, 2])):
                continue
            break
        if report_for == '1':
            generated = all_controls(CSP, platform, platform_url, timestamp)
            if not generated:
                continue
        elif report_for == '2':
            generated = policy_wise(CSP, platform, platform_url, timestamp)
            if not generated:
                continue
        user_input = input("\nDo you want to run it again?\nYes\nNo\n").lower()


if __name__ == "__main__":
    main()