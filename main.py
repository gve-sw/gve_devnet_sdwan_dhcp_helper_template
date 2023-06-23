"""
CISCO SAMPLE CODE LICENSE
                                  Version 1.1
                Copyright (c) 2020 Cisco and/or its affiliates

   These terms govern this Cisco Systems, Inc. ("Cisco"), example or demo
   source code and its associated documentation (together, the "Sample
   Code"). By downloading, copying, modifying, compiling, or redistributing
   the Sample Code, you accept and agree to be bound by the following terms
   and conditions (the "License"). If you are accepting the License on
   behalf of an entity, you represent that you have the authority to do so
   (either you or the entity, "you"). Sample Code is not supported by Cisco
   TAC and is not tested for quality or performance. This is your only
   license to the Sample Code and all rights not expressly granted are
   reserved.

   1. LICENSE GRANT: Subject to the terms and conditions of this License,
      Cisco hereby grants to you a perpetual, worldwide, non-exclusive, non-
      transferable, non-sublicensable, royalty-free license to copy and
      modify the Sample Code in source code form, and compile and
      redistribute the Sample Code in binary/object code or other executable
      forms, in whole or in part, solely for use with Cisco products and
      services. For interpreted languages like Java and Python, the
      executable form of the software may include source code and
      compilation is not required.

   2. CONDITIONS: You shall not use the Sample Code independent of, or to
      replicate or compete with, a Cisco product or service. Cisco products
      and services are licensed under their own separate terms and you shall
      not use the Sample Code in any way that violates or is inconsistent
      with those terms (for more information, please visit:
      www.cisco.com/go/terms).

   3. OWNERSHIP: Cisco retains sole and exclusive ownership of the Sample
      Code, including all intellectual property rights therein, except with
      respect to any third-party material that may be used in or by the
      Sample Code. Any such third-party material is licensed under its own
      separate terms (such as an open source license) and all use must be in
      full accordance with the applicable license. This License does not
      grant you permission to use any trade names, trademarks, service
      marks, or product names of Cisco. If you provide any feedback to Cisco
      regarding the Sample Code, you agree that Cisco, its partners, and its
      customers shall be free to use and incorporate such feedback into the
      Sample Code, and Cisco products and services, for any purpose, and
      without restriction, payment, or additional consideration of any kind.
      If you initiate or participate in any litigation against Cisco, its
      partners, or its customers (including cross-claims and counter-claims)
      alleging that the Sample Code and/or its use infringe any patent,
      copyright, or other intellectual property right, then all rights
      granted to you under this License shall terminate immediately without
      notice.

   4. LIMITATION OF LIABILITY: CISCO SHALL HAVE NO LIABILITY IN CONNECTION
      WITH OR RELATING TO THIS LICENSE OR USE OF THE SAMPLE CODE, FOR
      DAMAGES OF ANY KIND, INCLUDING BUT NOT LIMITED TO DIRECT, INCIDENTAL,
      AND CONSEQUENTIAL DAMAGES, OR FOR ANY LOSS OF USE, DATA, INFORMATION,
      PROFITS, BUSINESS, OR GOODWILL, HOWEVER CAUSED, EVEN IF ADVISED OF THE
      POSSIBILITY OF SUCH DAMAGES.

   5. DISCLAIMER OF WARRANTY: SAMPLE CODE IS INTENDED FOR EXAMPLE PURPOSES
      ONLY AND IS PROVIDED BY CISCO "AS IS" WITH ALL FAULTS AND WITHOUT
      WARRANTY OR SUPPORT OF ANY KIND. TO THE MAXIMUM EXTENT PERMITTED BY
      LAW, ALL EXPRESS AND IMPLIED CONDITIONS, REPRESENTATIONS, AND
      WARRANTIES INCLUDING, WITHOUT LIMITATION, ANY IMPLIED WARRANTY OR
      CONDITION OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-
      INFRINGEMENT, SATISFACTORY QUALITY, NON-INTERFERENCE, AND ACCURACY,
      ARE HEREBY EXCLUDED AND EXPRESSLY DISCLAIMED BY CISCO. CISCO DOES NOT
      WARRANT THAT THE SAMPLE CODE IS SUITABLE FOR PRODUCTION OR COMMERCIAL
      USE, WILL OPERATE PROPERLY, IS ACCURATE OR COMPLETE, OR IS WITHOUT
      ERROR OR DEFECT.

   6. GENERAL: This License shall be governed by and interpreted in
      accordance with the laws of the State of California, excluding its
      conflict of laws provisions. You agree to comply with all applicable
      United States export laws, rules, and regulations. If any provision of
      this License is judged illegal, invalid, or otherwise unenforceable,
      that provision shall be severed and the rest of the License shall
      remain in full force and effect. No failure by Cisco to enforce any of
      its rights related to the Sample Code or to a breach of this License
      in a particular situation will act as a waiver of such rights. In the
      event of any inconsistencies with any other terms, this License shall
      take precedence.
"""

import os, json, requests, time, urllib3, sys
from dotenv import load_dotenv

urllib3.disable_warnings()

# Authentication
def get_authenticated_session():
    host = os.environ['VMA_HOST']
    username = os.environ['VMA_USER']
    password = os.environ['VMA_PASS']

    session = requests.session()
    
    url = f"https://{host}/j_security_check"
    headers = {
        "Content-Type" : "application/x-www-form-urlencoded"
    }
    data = f"j_username={username}&j_password={password}"

    session.post(url, headers=headers, data=data, verify=False)

    return session

def get_xsrf_token(session, host):
    url = f"https://{host}/dataservice/client/token"
    headers = {
        "Content-Type" : "application/json"
    }
    return session.get(url, headers=headers).text

# Helper functions
def list_templates(session, host):
    url = f"https://{host}/dataservice/template/device"
    headers = {
        "Content-Type" : "application/json"
    }
    templates = session.get(url, headers=headers).json()['data']
    print("------")
    for temp in templates:
         print(f"Template Name: {temp['templateName']}")
         print(f"Template ID: {temp['templateId']}")
         print("------")

def get_devices_for_template(session, host, template_id):
    url = f"https://{host}/dataservice/template/device/config/attached/{template_id}"
    headers = {
        "Content-Type" : "application/json",
        "X-XSRF-TOKEN" : get_xsrf_token(session, host)
    }
    resp = session.get(url, headers=headers).json()
    result = []
    for entry in resp['data']:
        result += [entry['uuid']]
    
    return result

def get_devices_input(session, host, template_id, device_ids):
    url = f"https://{host}/dataservice/template/device/config/input"
    headers = {
        "Content-Type" : "application/json",
        "X-XSRF-TOKEN" : get_xsrf_token(session, host)
    }
    data = {
        "templateId" : template_id,
        "deviceIds" : device_ids,
        "isEdited" : False,
        "isMasterEdited" : False
    }
    resp = session.post(url, headers=headers, json=data).json()['data']
    return resp

# Set device template
def set_device_input(session, host, template_id, device_input):
    url = f"https://{host}/dataservice/template/device/config/attachfeature"

    headers = {
        "X-XSRF-TOKEN" : get_xsrf_token(session, host),
        "Content-Type" : "application/json"
    }

    data = {
      "deviceTemplateList" : [{
        "templateId": template_id,
        "device": device_input,
        "isEdited": False
      }]
    }

    resp = session.post(url, headers=headers, json=data).json()

    task_id = resp['id']
    url = f"https://{host}/dataservice/device/action/status/{task_id}"
    status_resp = session.get(url, headers=headers).json()

    if status_resp['validation']['statusId']=="failure":
       print("ERROR: "+ status_resp['validation']['currentActivity'])
       sys.exit(1)

    # Check on status updates
    while status_resp['summary']['status'] != "done":
      status_resp = session.get(url, headers=headers).json()
      print("------")
      print(f"DHCP helper setting status is \"{status_resp['summary']['status']}\" - Response: {json.dumps(status_resp['summary'], indent=2)}")
      time.sleep(5)   

if __name__ == "__main__":
        load_dotenv()
        host = os.environ['VMA_HOST']
        session = get_authenticated_session()

        list_templates(session,host)

        # Get user input
        input_string = input('Enter template id/ ids separated by a space: ')
        id_list = input_string.split()
        new_address=input('Enter the new dhcp address: ')
        print("------")

        # Set DHCP helper addresses
        for id in id_list:
            device_ids = get_devices_for_template(session, host, id)
            input = get_devices_input(session, host, id, device_ids)
            for device in input:
                # Set DHCP helper address
                # NOTE: This URL might change after configuration. Your vManage console shows the corresponding URL when hovering over the "DHCP helper" field in configuring your device template configuration page (Configuration > Templates > Device Templates)
                device["/0/GigabitEthernet0/0/0.75/interface/dhcp-helper"] = new_address
            set_device_input(session, host, id, input)
