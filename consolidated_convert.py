import json
from airium import Airium
import datetime
import sys
import os

def get_header(head):
    x = 0
    for i in head:
        if i.isupper():
            x = head.index(i)
            break
    return head[:x].capitalize() + " " +  head[x:].capitalize()


def dict_found(i, element, a):
    t = dict(i[element])
    with a.p(id=element):
        a.strong(_t=element.capitalize())
        with a.ul():
            for key in t.keys():
                if type(t[key]) == type([]):
                    with a.li():
                        a.strong(_t=f"{key.capitalize()} : ")
                        list_found(t[key], key, a)
                else:
                    with a.li():
                        a.strong(_t=key.capitalize())
                        a(f" : {i[element][key]}")


def list_found(i, a):
    with a.ul():
        for item in i:
            with a.li():
                a(f"{item}")


def getEvaluation(evaluation, a):
    with a.th():
        with a.ul():
            for i in evaluation:
                if evaluation[i] != []:
                    with a.li():
                        a(f"{i} : {evaluation[i]}")


def convert_to_html(CSP, timestamp, policy, is_policy):
    path = "Resposnes"
    if os.path.exists(CSP):
        pass
    else:
        os.mkdir(CSP)
    if is_policy:
        file = open(f"{path}/{policy}_{timestamp}.json")
        if os.path.exists(f"{CSP}/Policies"):
            pass
        else:
            os.mkdir(f"{CSP}/Policies")
        write_file_path = f"{CSP}/Policies/{policy}_{timestamp}.html"
    else:
        file = open(f"{path}/{CSP}_response_{timestamp}.json")
        write_file_path = f"{CSP}/Static_Content_{CSP}_{timestamp}.html"
    file_json = json.load(file)



    with open(write_file_path, "w") as f:
        a = Airium()
        a('<!DOCTYPE html>')
        with a.html(lang="en"):
            with a.head():
                a.meta(charset="utf-8")
                a.title(_t=f"Static_Content_{CSP}")
                a.style(_t="""table {
                                  border: 1px solid black;
                                  align: left;
                                  text-align: left;
                                  width : 100%;
                              }
                              th, td {
                                  border: 1px solid black;
                                  align: left;
                                  text-align: left;
                              }""")

            with a.body():
                with a.h4():
                    a(f"Report Generated Time : {datetime.datetime.now()}")
                with a.h2():
                    a(f"Qualys CloudView Controls Metadata")
                if file_json['control'] == []:
                    print(f"No controls in Policy - {policy}")
                    with a.h4():
                        a(f"No controls in Policy - {policy}")
                else:
                    with a.h3():
                        a(f"Index for Controls in {policy if is_policy else ''} Document")
                for i in file_json['control']:
                    with a.a(href=f"#{i['cid']}"):
                        a(f"CID - {i['cid']} : {i['controlName']}")
                        a("<br>")

                item = len(file_json['control'])
                # setup toolbar
                complete_percent = 0
                process = f"Generating Files {CSP}...  "
                sys.stdout.write(f"{process}")
                sys.stdout.flush()

                for i in file_json['control']:
                    i.pop("workflowBased")
                    i.pop("remediationEnabled")

                    with a.h3(id=int(i['cid'])):
                        a(f"CID - {i['cid']} : {i['controlName']}")
                    with a.table():
                        for element in i:
                            # if element in ["cid", "controlType", "provider", "controlName", "criticality", "resourceType", "evaluation", "manualRemediation", "buildTimeRemediation", ]:
                            if element == "evaluation":
                                with a.tr():
                                    a.th(_t=get_header(element))
                                    getEvaluation(i[element], a)
                                continue
                            with a.tr():
                                a.th(_t=get_header(element))
                                a.th(_t=i[element])

                    if complete_percent != int(((file_json['control'].index(i) + 1) / item) * 100):
                        sys.stdout.write("\b" * (len(str(complete_percent)) + 1))
                        complete_percent = int(((file_json['control'].index(i) + 1) / item) * 100)
                        sys.stdout.write(str(complete_percent) + "%")
                        sys.stdout.flush()

                sys.stdout.write("\n")
                with a.h4():
                    a(f"Report Generated Time : {datetime.datetime.now()}")

        f.write(str(a))
