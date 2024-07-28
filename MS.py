#!/usr/bin/python3
# C:\Program Files\Python37\
#
#        Origins: Stonebranch GmbH
#        Author: Ioanna Kyriazidou
#                Karthik Mohan
#
#        Version History:    1.0     IK     07-Nov-2019     Initial Version (
#                            Notification Functionality)
#                            2.0     KM     03-Mar-2020     Adding
#                            Approval Functionality
#                            2.1     KM     23-Sep-2020 Variablizied Parameters
#
#    Copyright (c) Stonebranch GmbH, 2019.  All rights reserved.
#
#    The copyright in this work is vested in Stonebranch.
#    The information contained in this work (either in whole or in part)
#    is confidential and must not be modified, reproduced, disclosed or
#    disseminated to others or used for purposes other than that for which
#    it is supplied, without the prior written permission of Stonebranch.
#    If this work or any part hereof is furnished to a third party by
#    virtue of a contract with that party, use of this work by such party
#    shall be governed by the express contractual terms between Stonebranch,
#    which is party to that contract and the said party.
#
#    The information in this document is subject to change without notice
#    and should not be construed as a commitment by Stonebranch. Stonebranch
#    assumes no responsibility for any errors that may appear in this document.
#    With the appearance of a new version of this document all older versions
#    become invalid.
#
# Importing required packages
import logging
import sys
import argparse
import uuid
import time
import datetime
import json
import re
import urllib3
import requests

version = "2.1"


# initialize() function helps to parse the arguments passed form the
# Universal Controller
def initialize():
    global argparse, logging, sys, requests, uuid, time, datetime, json, re, \
        log_date, args
    parser = argparse.ArgumentParser(
        description='Purpose : Teams Notification Universal Task')
    # ## --> Capture Universal Task Form Variables Here
    parser.add_argument("--uc_teams_function",
        default="${ops_mst_teams_function}")
    parser.add_argument("--uc_job_name", default="${ops_mst_jobname}")
    parser.add_argument("--uc_job_status", default="${ops_mst_jobstatus}")
    parser.add_argument("--uc_teams_incoming_webhook",
        default="${ops_mst_teams_webhook}")
    parser.add_argument("--uc_exec_user", default="${ops_mst_exec_user}")
    parser.add_argument("--uc_job_type", default="${ops_mst_jobtype}")
    parser.add_argument("--uc_title", default="${ops_mst_title}")
    parser.add_argument("--uc_text", default="${ops_mst_text}")
    parser.add_argument("--uc_api_endpoint", default="${ops_mst_api_endpoint}")
    # parser.add_argument("--UC_description", default="${ops_mst_description}")
    # ## -->
    parser.add_argument("--logginglevel", default="${ops_logic_logginglevel}")
    args = parser.parse_args()
    # -- Setup Logging
    numeric_level = getattr(logging, args.logginglevel.upper(), None)
    logging.basicConfig(format='%(asctime)-15s - %(levelname)-8s - %(message)s',
        level=logging.INFO)
    # -- Print Paramater Values
    logging.debug(
        "Executing version {0} with the following parameters : {1}".format(
            version, args))
    # -- Ignore Https Warnings
    urllib3.disable_warnings()
    # -- Setup LogDate for Trigger Log Search
    log_date = json.dumps(datetime.datetime.now().isoformat())


# approval_notification() function helps to send approval notification to the
# teams incoming web-channel
def approval_notification():
    print("Approval Function for Teams")
    webhook = args.uc_teams_incoming_webhook
    team_data = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": "This is the summary property",
        "themeColor": "#008000",
        "sections": [
            {
                "activityTitle": "**Pending approval**"
            },
            {
                "startGroup": True,
                "title": "" + args.uc_title,
                "color": "10,10,10",
                "activityTitle": "**Approval Needed for:** " + args.uc_job_name,
                "activitySubtitle": "Please review the approval request",
                "facts": [
                    {
                        "name": "Job Status:",
                        "value": "" + args.uc_job_status
                    },
                    {
                        "name": "Executed by:",
                        "value": "" + args.uc_exec_user
                    },
                ]
            },
            {
                "potentialAction": [
                    {
                        "@type": "ActionCard",
                        "name": "Approve",
                        "color": "#008000",
                        "inputs": [
                            {
                                "@type": "TextInput",
                                "id": "comment",
                                "isMultiline": True,
                                "title": "Reason (optional)"
                            }
                        ],
                        "actions": [
                            {
                                "@type": "HttpPOST",
                                "name": "Submit",
                                "target": "" + args.uc_api_endpoint,
                                "body": "Approved" + ":" + args.uc_job_name,
                                "CARD-UPDATE-IN-BODY": True,
                                "CARD-ACTION-STATUS": "The Request is "
                                                      "Approved for the "
                                                      "Task:" + args.uc_job_name
                            }
                        ]
                    },
                    {
                        "@type": "ActionCard",
                        "name": "Reject",
                        "inputs": [
                            {
                                "@type": "TextInput",
                                "id": "comment",
                                "isMultiline": True,
                                "title": "Reason (optional)"
                            }
                        ],
                        "actions": [
                            {
                                "@type": "HttpPOST",
                                "name": "Submit",
                                "target": "" + args.uc_api_endpoint,
                                "body": "Rejected" + ":" + args.uc_job_name,
                                "CARD-UPDATE-IN-BODY": True,
                                "CARD-ACTION-STATUS": "The Request is "
                                                      "Rejectec for the "
                                                      "Task:" + args.uc_job_name
                            }
                        ]
                    }
                ]
            },
        ]
    }
    response = requests.post(webhook, data=json.dumps(team_data),
        headers={'Content-Type': 'application/json'})
    print(response.status_code)


# send_notification() function helps to send task notification to the
# teams incoming web-channel
def send_notification():
    print("Notification Function for Microsoft Teams")
    webhook = args.uc_teams_incoming_webhook
    team_notification_data = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": "This is the summary property",
        "themeColor": "0075FF",
        "sections": [
            {
                "activityTitle": "" + args.uc_title,
                "activitySubtitle": "" + args.uc_text
            },
            {
                "startGroup": True,
                "title": "**Notification for Microsoft Teams**",
                "facts": [
                    {
                        "name": "Job Status:",
                        "value": "" + args.uc_job_status
                    },
                    {
                        "name": "Executed by:",
                        "value": "" + args.uc_exec_user
                    },
                ]
            },
        ]
    }
    response = requests.post(webhook, data=json.dumps(team_notification_data),
        headers={'Content-Type': 'application/json'})
    print(response.status_code)


if __name__=="__main__":
    logging.info("Microsoft Teams Notifications process started...")
    initialize()
    logging.info("Initialzing complete")
    if args.uc_teams_function=="Send Message":
        logging.info("Prepare message for Teams Channel")
        send_notification()
        logging.info("Microsoft Teams Notifications process finished...")
    if args.uc_teams_function=="Approval Notification":
        logging.info("Prepare Approval Notification for Teams Channel")
        approval_notification()