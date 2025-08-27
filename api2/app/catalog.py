# catalog.py

# Common urgency levels for all ticket types
URGENCY_LEVELS = ["critical", "high", "medium", "low"]

# Loan Tape
TYPE_OF_RERUN_LOAN_TAPE = ["final", "estimated"]
VENDORS_LOAN_TAPE = [
  "AAA Final Loan Tape",
  "Bawag Crb Final Loan Tape",
  "Bawag Final Loan Tape",
  "Bayview Asset Management Final Loan Tape",
  "Blackstone Final Loan Tape",
  "Colchis Final Loan Tape",
  "Congressional Bank Final Loan Tape",
  "Credigy Final Loan Tape",
  "CSAM Final Loan Tape",
  "Davidson and Kempner Final Loan Tape",
  "Edge Focus Final Loan Tape",
  "Fasanara Final Loan Tape",
  "Ibi Final Loan Tape",
  "Magnetar Final Loan Tape",
  "Maples Final Loan Tape",
  "Morgan Stanley Final Loan Tape",
  "NeNet Final Loan Tape",
  "O'Connor Final Loan Tape",
  "Pagaya Final Loan Tape",
  "Phoenix Final Loan Tape",
  "Pimco Final Loan Tape",
  "Smart Lenders Final Loan Tape",
  "Sound Point Final Loan Tape",
  "Stone Ridge Final Loan Tape",
  "Theorem Final Loan Tape",
  "Vervent Final Loan Tape",
  "Colchis Estimated Loan Tape",
  "Congressional Bank Estimated Loan Tape",
  "Credigy Estimated Loan Tape",
  "CSAM Estimated Loan Tape",
  "Davidson and Kempner Estimated Loan Tape",
  "Edge Focus Estimated Loan Tape",
  "Fasanara Estimated Loan Tape",
  "Ibi Estimated Loan Tape",
  "Magnetar Estimated Loan Tape",
  "Maples Estimated Loan Tape",
  "Morgan Stanley Estimated Loan Tape",
  "NeNet Estimated Loan Tape",
  "O'Connor Estimated Loan Tape",
  "Phoenix Estimated Loan Tape",
  "Pimco Estimated Loan Tape",
  "Smart Lenders Estimated Loan Tape",
  "Sound Point Estimated Loan Tape",
  "Theorem Final Estimated Loan Tape",
]


# Investor Reporting Incident
TYPE_OF_RERUN_INVESTOR = [
    "investor reporting manual rerun",
    "final loan tape rerun",
    "none"
]

# Investor Reports Manual Rerun
NON_ORIGINATION_TYPES = ["loan history", "loan transaction", "ucc", "none of the above"]
ORIGINATION_TYPES = [
    "previous day originations custom extended",
    "previous day originations",
    "none of the above"
]

# Manual Loan Verifications
FROM_INVESTORS_MANUAL_LOAN_VERIFICATIONS = [
  "Marlette",
  "1st Capital Bank",
  "AAA",
  "Blackstone",
  "Blue Ridge Bank",
  "Carval",
  "Citi",
  "Securitization",
  "Colchis",
  "Community First",
  "Congressional Bank",
  "CRB Standard",
  "Credigy",
  "Credit Suisse",
  "Customer Bank",
  "Davidson Kempner Standard",
  "Drummond Bank",
  "Duff and Phelps Standard",
  "DV01",
  "Edge Focus Custom",
  "Edge Focus Standard",
  "Exigent",
  "Fasanara",
  "First Freedom",
  "Fortress",
  "Four Corners",
  "Goldman",
  "IBI Consumer Credit, LP",
  "Marion Center Bank",
  "Millenium",
  "Moore Capital",
  "Morgan Stanley Standard",
  "NelNet",
  "Pagaya 2020-4 v2",
  "Pagaya 2021-1 v2",
  "Pagaya 2021-2 v2",
  "Pagaya 2021-4 v2",
  "Pagaya 2021-5 v2",
  "Pagaya 2021-HG1 v2",
  "Pagaya 2022-1 v2",
  "Pagaya 2022-2 v2",
  "Pagaya 2022-4 v2",
  "Pagaya 2022-5 v2",
  "Pagaya 2022-6 v2",
  "Pagaya 2023-2 v2",
  "Pagaya 2023-3 v2",
  "Pagaya 2023-4",
  "Pagaya 2023-5",
  "Pagaya 2023-6",
  "Pagaya 2023-7",
  "Pagaya Acquisition Trust V2",
  "Pagaya DEBT SALES v2",
  "Pagaya FUNDING TRUST v2",
  "Pagaya Optimum v2",
  "Pagaya PAID 2023-1 v2",
  "Pagaya PAID v2",
  "Pagaya PAT v2",
  "Pagaya PFTII v2",
  "Pagaya PSHT v2",
  "Peeriq Standard",
  "Pimco",
  "Resurgent",
  "Smart Lenders",
  "Sound Point",
  "Stoneridge 2020-1 v2",
  "Stoneridge 2020-2 v2",
  "Stoneridge 2021 Lendx v2",
  "Stoneridge 2021-M1 v2",
  "Stoneridge 2021-M2 v2",
  "Stoneridge 2021-N1 v2",
  "Stoneridge 2022-1 v2",
  "Stoneridge 2022-2 v2",
  "Stoneridge 651 v2",
  "Stoneridge Alternative v2",
  "Stoneridge Issuer 1 v2",
  "Stoneridge Issuer 2 v2",
  "Stoneridge Issuer 2023-1 v2",
  "The Phoenix",
  "The Phoenix AMITIM",
  "The Phoenix Insurance Group",
  "Theorem 2022-3 v2",
  "Theorem 2023-1"
  "Theorem 2023-2",
  "Theorem Bulk 345 v2",
  "Theorem Custom Product v2",
  "Theorem GS Trust",
  "Theorem Main Fund Trust II",
  "Theorem Main v2",
  "Theorem Opportunities Fund",
  "Theorem Prime Plust Fund Trust II",
  "Theorem Prime Plus v2",
  "Theorem Securitization Reporting v2",
  "Unity Bank",
  "Investor is not listed"
]
TO_RECIPIENTS_MANUAL_LOAN_VERIFICATIONS = [
  "1st Capital Bank",
  "AAA",
  "Arcesium",
  "Blackstone",
  "Cardio AI",
  "Carval",
  "Citi",
  "Colchis",
  "Community First",
  "Congressional Bank",
  "CRB",
  "Credigy",
  "Credit Suisse",
  "Customer Bank",
  "Drummond Bank",
  "Duff and Phelps",
  "DV01",
  "Edge Focus",
  "Exigent",
  "Fasanara",
  "First Freedom",
  "Four Corners",
  "Goldman",
  "IBI Consumer Credit, LP",
  "Maples",
  "Marion Center Bank",
  "Millenium",
  "Moore Capital",
  "Morgan Stanley",
  "NelNet",
  "Peeriq",
  "Peeriq s3",
  "Resurgent",
  "Situs",
  "Smart Lenders",
  "Sound Point",
  "SSC",
  "The Phoenix",
  "Theorem",
  "Unity Bank",
  "US Bank",
  "Wilmington",
  "Recipient not listed"
]

# SFTP Requests
INVESTORS_SFTP_REQUESTS = [
  "Bawag",
  "Carval",
  "Citi",
  "Citi Securitization",
  "Colchis",
  "Community First",
  "Congressional Bank",
  "Credigy",
  "Customer Bank",
  "Duff and Phelps",
  "DV01",
  "Even Financial",
  "Figure",
  "Freedom",
  "Genesys",
  "Goldman",
  "IBI Capital",
  "Magnetar",
  "Maples",
  "Millenium",
  "Millenium MS",
  "Morgan Stanley",
  "Nav Consulting",
  "Navient",
  "Navient 2",
  "Orchard",
  "Pagaya",
  "Peer IQ",
  "Pimco",
  "Quinnstreet Affiliate Reporting",
  "Resurgent",
  "Situs",
  "Smart Lenders",
  "Soros",
  "SST",
  "The Phoenix",
  "Theorem",
  "Top 10",
  "US Bank",
  "Vervent",
  "Viteos",
  "Wilmington Trust",
  "WSFS",
  "Zero Variance",
  "Investor is not listed"
]

# Generic Document Verification DRqwerqwerqwerqqqq
INVESTORS_GENERIC = [
  "Pimco",
  "Pagaya",
  "NelNet",
  "Liberty Mutual",
  "Theorem",
  "Stoneridge",
  "Fortress",
  "Blue Ridge Bank",
  "Goldman"
]
# --------------------
# Datadog
# --------------------
SOURCE_TYPES = ["k8s", "lambda", "other"]
SERVICE_FIELDS = ["datadog logs", "cloud watch metrics", "sumo logs", "cloud watch logs", "datadog metrics", "other"]  # no fixed options yet
INFRASTRUCTURE_TYPES = ["kubernetes", "lambda", "database", "other aws srvices"]
SOURCE_METRICS = ["datadog logs", "cloud watch metrics", "sumo logs", "cloud watch logs", "datadog metrics", "other"]
ALERT_PRIORITIES = ["P1: Critical", "P2: High", "P3: Medium", "P4: Low", "P5: Info"]
ENVIRONMENTS = ["prd", "sbx", "uat"]

# --------------------
# GoAnywhere
# --------------------
PRIORITY_LEVELS_ADHOC = ["Low", "Medium", "High", "Urgent"]
TRANSFER_TYPES = ["One-time Transfer", "Recurring Transfer"]
FREQUENCY = ["daily", "weekly", "monthly"]
SFTP_OR_S3 = ["sftp", "s3 bucket"]

# --------------------
# JAMS
# --------------------
JAMS_REQUEST_TYPES = ["Add or Create a new Job/Sequence", "Change or Modify an Existing Job/Setup", "Delete an Existing Job/Setup", "Hold a Job or Sequence"]
AGENT_NODES = ["utility.marlettefunding.com", "prd-sas03.marlettefunding.com", "sas-app-jobs.marlette.ad", "PRD-JAMS01", "uat-docker-jams-nlb-ce0d419dc754d783.elb.us-east-1.amazonaws.com", "ip-10-71-142-13.ec2.internal", "ip-10-90-59-61.ec2.internal"]  # fill with actual list later
PRIORITY_JAMS = ["Low", "Medium", "High", "N/A"]
JOB_FREQUENCY = ["daily", "weekly", "monthly", "n/a"]

# --------------------
# Config Changes
# --------------------
CHANGE_TYPES = ["add", "update", "remove"]

# --------------------
# SFTP / Investors
# --------------------
# SFTP Migration and New Connectivity
AUTHENTICATION_TYPES = ["ssh key", "password"]
SFTP_TYPES = ["basic sftp", "sftp with ssh key authentication"]
ENCRYPTION_METHODS = ["AES-128", "AES-192", "AES-256", "RSA", "DES", "3DES", "Blowfish"]


{
  "department": [
    "Dialer & WFM Services",
    "Enterprise Risk Management",
    "Facilities Services",
    "Human Resources Services",
    "Intranet & Communications",
    "Intake Requests",
    "InfoSec Service Desk",
    "IT Services",
    "SRE/Production Support",
    "Technology Change Request"
  ],
  "categories": {
    "SRE/Production Support": {
      "Financial Service Request": [
        {
          "ticket_type": "Loan Tape",
          "description": "",
          "fields": [
            { "name": "email", "type": "string", "description": "" },
            { "name": "summary", "type": "string", "description": "" },
            { "name": "description", "type": "string", "description": "" },
            {
              "name": "urgency",
              "type": "choice",
              "options": URGENCY_LEVELS,
              "description": ""
            },
            { "name": "request_date", "type": "date", "description": "" },
            {
              "name": "vendor_name",
              "type": "choice",
              "options_source": VENDORS_LOAN_TAPE,
              "description": ""
            },
            {
              "name": "type_of_rerun",
              "type": "choice",
              "options": TYPE_OF_RERUN_LOAN_TAPE,
              "description": ""
            }
          ]
        },
        {
          "ticket_type": "Investor Reporting Incident",
          "description": "",
          "fields": [
            { "name": "email", "type": "string", "description": "" },
            { "name": "summary", "type": "string", "description": "" },
            { "name": "description", "type": "string", "description": "" },
            {
              "name": "urgency",
              "type": "choice",
              "options": URGENCY_LEVELS,
              "description": ""
            },
            {
              "name": "type_of_rerun",
              "type": "choice",
              "options": TYPE_OF_RERUN_INVESTOR,
              "description": ""
            }
          ]
        },
        {
          "ticket_type": "Investor Reports Manual Rerun",
          "description": "",
          "fields": [
            { "name": "email", "type": "string", "description": "" },
            { "name": "start_date", "type": "date", "description": "" },
            { "name": "end_date", "type": "date", "description": "" },
            { "name": "investor_to_recipient", "type": "int", "description": "" },
            {
              "name": "non_origination_types",
              "type": "multi_choice",
              "options": NON_ORIGINATION_TYPES,
              "description": "Type of master reports - non origination types"
            },
            {
              "name": "origination_types",
              "type": "multi_choice",
              "options": ORIGINATION_TYPES,
              "description": "Type of master reports - origination types"
            },
            { "name": "new_investor_name", "type": "string", "description": "" },
            { "name": "vendor_related", "type": "bool", "description": "Is this request vendor related? Example: The vendor has not received th requested reports" },
            { "name": "subpool_or_update_related", "type": "bool", "description": "Is this request related to a subpool or other update?: Example: Has a subpool been updated or other update(s) made?" },
            { "name": "previous_incident_related", "type": "bool", "description": "Is this request a result of a previous incident or failure? Example: Job failure or scheduled delay" },
            { "name": "rerun_master_reports", "type": "bool", "description": "Has there been a change of data on the backend?" }
          ]
        },
        {
          "ticket_type": "Manual Loan Verifications",
          "description": "",
          "fields": [
            { "name": "email", "type": "string", "description": "" },
            {
              "name": "from_investor",
              "type": "choice",
              "options_source": FROM_INVESTORS_MANUAL_LOAN_VERIFICATIONS,
              "description": ""
            },
            {
              "name": "to_recipient",
              "type": "choice",
              "options_source": TO_RECIPIENTS_MANUAL_LOAN_VERIFICATIONS,
              "description": ""
            },
            { "name": "naming_convention", "type": "string", "description": "Naming convention for file. E.g. 'LoanAgreement_mft2021d_YYYYMMDD'" },
            { "name": "files", "type": "files", "description": "Please upload the files to be verified" }
          ]
        },
        {
          "ticket_type": "SFTP Requests",
          "description": "",
          "fields": [
            { "name": "email", "type": "string", "description": "" },
            {
              "name": "from_investor",
              "type": "choice",
              "options_source": INVESTORS_SFTP_REQUESTS,
              "description": "Investor to send the transfer"
            },
            {
              "name": "to_recipient",
              "type": "choice",
              "options_source": INVESTORS_SFTP_REQUESTS,
              "description": "Recipient to receive the transfer"
            },
            { "name": "sftp_s3_remote_folder", "type": "rich_text", "description": r"E.g sftp://example.com/path or s3://bucket-name/path" },
            { "name": "encryption_required", "type": "bool", "description": "Is encryption required before transfer?" },
            { "name": "files", "type": "files", "description": "Attach files for SFTP transfer." },
            { "name": "investor_name", "type": "string", "description": "If investor is not listed, input new investor name below." },
            { "name": "box_file_location", "type": "rich_text", "description": r"E.g. Box\Capital Market Dept\Finance Outgoing Files\Investor Handoffs SFTP\CRB\2024.03" }
          ]
        },
        {
          "ticket_type": "Generic Document Verification DR",
          "description": "",
          "fields": [
            { "name": "email", "type": "string", "description": "" },
            { "name": "summary", "type": "string", "description": "" },
            { "name": "description", "type": "string", "description": "" },
            {
              "name": "urgency",
              "type": "choice",
              "options": URGENCY_LEVELS,
              "description": ""
            },
            { "name": "run_date", "type": "date", "description": "" },
            {
              "name": "investor_name",
              "type": "choice",
              "options_source": INVESTORS_GENERIC,
              "description": ""
            }
          ]
        }
      ],
      "IT Service Requests": [
        {
          "ticket_type": "Datadog Log Rehydration",
          "description": "Use this request to retrieve logs in Datadog that are older than 7 days.",
          "fields": [
            { "name": "email", "type": "string", "description": "" },
            { "name": "summary", "type": "string", "description": "" },
            { "name": "scope_of_work", "type": "string", "description": "" },
            {
              "name": "source",
              "type": "choice",
              "options": SOURCE_TYPES,
              "description": ""
            },
            {
              "name": "service_field",
              "type": "choice",
              "options_source": SERVICE_FIELDS,
              "description": "Service logs which are needed to rehydrate"
            },
            { "name": "start_date", "type": "date", "description": "" },
            { "name": "end_date", "type": "date", "description": "" },
            { "name": "log_query_message_level", "type": "string", "description": "Any further log query/details that will narrow down the backfill." },
            { "name": "start_time", "type": "time", "description": "" },
            { "name": "end_time", "type": "time", "description": "" }
          ]
        },
        {
          "ticket_type": "Datadog Log Setup/Troubleshooting",
          "description": "Intake for general log setup/troubleshooting requests. This covers issues with logs not showing in Datadog platform or setting up some new logs.",
          "fields": [
            { "name": "email", "type": "string", "description": "" },
            { "name": "summary", "type": "string", "description": "" },
            { "name": "scope_of_work", "type": "string", "description": "Please enter some more details on the issue you are facing or desired outcomes that you need help with." },
            {
              "name": "source",
              "type": "choice",
              "options": SOURCE_TYPES,
              "description": "Source of the logs"
            },
            {
              "name": "service_field",
              "type": "choice",
              "options_source": SERVICE_FIELDS,
              "description": "Name of the service for logs."
            }
          ]
        },
        {
          "ticket_type": "Datadog Monitors and Dashboards",
          "description": "For configuration or assistance with Datadog features (logging, tracing etc.). Also to request a Datadog monitor, alert, or dashboard.",
          "fields": [
            { "name": "email", "type": "string", "description": "" },
            { "name": "summary", "type": "string", "description": "" },
            { "name": "description", "type": "rich_text", "description": "" },
            { "name": "scope_of_work", "type": "string", "description": "" },
            { "name": "infrastructure_type", "type": "choice", "options_source": INFRASTRUCTURE_TYPES, "description": "" },
            { "name": "pod_name", "type": "string", "description": "" },
            { "name": "type_of_source_metric", "type": "choice", "options_source": SOURCE_METRICS, "description": "Source of error or informational data. i.e aws metrics, sumo logs, or other" },
            { "name": "env", "type": "choice", "options": ENVIRONMENTS, "description": "" },
            { "name": "alert_priority", "type": "choice", "options": ALERT_PRIORITIES, "description": "" },
            { "name": "service_name", "type": "string", "description": "" },
            { "name": "alert_slack_channel", "type": "string", "description": "What Slack Channel would you like to receive these alerts?" },
            { "name": "alert_threshold", "type": "string", "description": "What is the threshhold for your metric/log that you want to be notified?" },
            { "name": "tags", "type": "string", "description": "Please include any custom identifying tags" }
          ]
        },
        {
          "ticket_type": "GoAnywhere File Transfer Ad Hoc Request",
          "description": "This form is intended to streamline requests for ad hoc file transfers using GoAnywhere Managed File Transfer solution. It collects all necessary information to facilitate secure and efficient file transfers between internal and external parties.",
          "fields": [
            { "name": "email", "type": "string", "description": "" },
            { "name": "summary", "type": "string", "description": "" },
            { "name": "job_title", "type": "string", "description": "Name of the existing Ad Hoc GoAnywhere Job" },
            { "name": "reason_for_adhoc_run", "type": "rich_text", "description": "Provide a detailed explanation for the ad hoc transfer" },
            { "name": "priority_level", "type": "choice", "options": PRIORITY_LEVELS_ADHOC, "description": "Select urgency level" },
            { "name": "requested_completion_date", "type": "date", "description": "When would you like this job completed?" },
            { "name": "transfer_type", "type": "choice", "options": TRANSFER_TYPES, "description": "" },
            { "name": "frequency", "type": "choice", "options": FREQUENCY, "description": "" },
            { "name": "additional_information", "type": "rich_text", "description": "" },
            { "name": "reqquestor_email", "type": "string", "description": "PLease enter requestor's email to forward GoAnywhere success or failure email." }
          ]
        },
        {
          "ticket_type": "GoAnywhere Request PRD",
          "description": "For assistance with new or existing GoAnywhere Managed File Transfer project(s). Also for support and monitoring for a GoAnywhere Managed File Transfer file transfer",
          "fields": [
            { "name": "email", "type": "string", "description": "" },
            { "name": "summary", "type": "string", "description": "" },
            { "name": "sftp_or_s3", "type": "choice", "options": SFTP_OR_S3, "description": "" },
            { "name": "job_name", "type": "string", "description": "" }
          ]
        },
        {
          "ticket_type": "GoAnywhere Request UAT",
          "description": "For assistance with new or existing GoAnywhere User Acceptance Testing Managed File Transfer project(s). Also for support for a GoAnywhere Managed File Transfer file transfer",
          "fields": [
            { "name": "email", "type": "string", "description": "" },
            { "name": "summary", "type": "string", "description": "" },
            { "name": "sftp_or_s3", "type": "choice", "options": SFTP_OR_S3, "description": "" },
            { "name": "job_name", "type": "string", "description": "" }
          ]
        },
        {
          "ticket_type": "JAMS Batch Job Request",
          "description": "Support for monitoring and/or configuration of a new or existing job. Also for assistance with JAMS licensing and configurations. This request type is used to initiate modifictaions to Batch Operations Jobs or Sequences, including but not limited to: adding new jobs, placing jobs on hold, deleting existing jobs, or making updates to scheduling parameters. Please provide detailed information regarding the specific change needed to ensure timely and accurate processing.",
          "fields": [
            { "name": "email", "type": "string", "description": "" },
            { "name": "summary", "type": "string", "description": "" },
            { "name": "request_type", "type": "choice", "options": JAMS_REQUEST_TYPES, "description": "Select the type of request you are making" },
            { "name": "agent_nodes", "type": "choice", "options_source": AGENT_NODES, "description": "Select the agent nodes where the job should run" },
            { "name": "priority", "type": "choice", "options": PRIORITY_JAMS, "description": "Job's Priority for Xmatters Alert." },
            { "name": "job_frequency", "type": "choice", "options": JOB_FREQUENCY, "description": "Daily, Weekly, Monthly" },
            { "name": "job_name", "type": "rich_text", "description": "If applicable, provide the name of the job(s) to be modified or deleted." },
            { "name": "user_name", "type": "string", "description": "User Account Credentials" },
            { "name": "scheduled_date", "type": "date", "description": "Date the job should execute" },
            { "name": "scheduled_time", "type": "time", "description": "Time the job should execute" },
            { "name": "upstream_job", "type": "string", "description": "Are there any jobs that must be completed before this job?" },
            { "name": "downstream_job", "type": "string", "description": "Are there any jobs that depend on the completion of this job?" },
            { "name": "pod_and_lead_engineer", "type": "string", "description": "In the event of an incident, who should be notified?" },
            { "name": "additional_information", "type": "rich_text", "description": "Provide any additional details or instructions related to this request" }
          ]
        },
        {
          "ticket_type": "Request for global Configuration YAML File Update",
          "description": "Use this form to request changes to global configuration YAML files. Provide details about the modification, environment, and any potential impact. Include a rollback plan and attach relevant files for approval and processing.",
          "fields": [
            { "name": "email", "type": "string", "description": "" },
            { "name": "summary", "type": "string", "description": "" },
            { "name": "requestor_name", "type": "string", "description": "Name of the person submitting this change." },
            { "name": "change_type", "type": "choice", "options": CHANGE_TYPES, "description": "What kind of change is required?" },
            { "name": "proposed_change", "type": "rich_text", "description": "Describe the change/update or upload the update YAML file." },
            { "name": "reason_for_change", "type": "string", "description": "Why is this change/update needed?" },
            { "name": "impact", "type": "bool", "description": "Does this change/update affect anything else?" },
            { "name": "description_of_change", "type": "string", "description": "Short description of the change" }
          ]
        },
        {
          "ticket_type": "SFTP Migration",
          "description": "Use this form to request the migration of an existing SFTP connection to a new server. Please provide details for both the old and new servers, authentication methods, and encryption settings. Include a timeline for testing and any additional information to ensure smooth transition.",
          "fields": [
            { "name": "email", "type": "string", "description": "" },
            { "name": "summary", "type": "string", "description": "" },
            { "name": "investor_name", "type": "string", "description": "The unique identifier or name of the investor for whom the SFTP migration is being implemented." },
            { "name": "old_sftp_server_address", "type": "string", "description": "The URL or IP address of the existing SFTP server." },
            { "name": "old_port_number", "type": "string", "description": "The port number used to connect to the existing SFTP server." },
            { "name": "old_path_directory", "type": "string", "description": "The specific directory path on the existing SFTP server where files are currently uploaded/downloaded." },
            { "name": "reason_for_migration", "type": "rich_text", "description": "briefly describe the reason for migrating from the old SFTP server" },
            { "name": "new_sftp_server_address", "type": "string", "description": "The URL or IP address of the new SFTP server." },
            { "name": "new_port_number", "type": "string", "description": "The port number used to connect to the new SFTP server." },
            { "name": "new_path_directory", "type": "string", "description": "The specific directory path on the new SFTP server where files should be uploaded/downloaded." },
            { "name": "authentication_type", "type": "choice", "options": AUTHENTICATION_TYPES, "description": "Specify the authentication method to be used" },
            { "name": "username", "type": "string", "description": "Username required for SFTP access" },
            { "name": "password", "type": "string", "description": "The password associated with the username" },
            { "name": "encryption_method", "type": "choice", "options": ENCRYPTION_METHODS, "description": "Specify encryption method used" },
            { "name": "validation_date", "type": "date", "description": "Date by which the migration should be validated and tested" },
            { "name": "validation_time", "type": "time", "description": "Time by which the migration should be validated and tested" },
            { "name": "scope_of_work", "type": "rich_text", "description": "" },
            { "name": "ssh_key", "type": "file", "description": "Upload the SSH key file if SSH key authentication is used." },
            { "name": "encryption_key", "type": "file", "description": "upload the encryption key file if one is available for secure communication" },
            { "name": "notification_email", "type": "string", "description": "Email address where notifications about the migration status should be sent" },
            { "name": "additional_information", "type": "rich_text", "description": "Any additional details" },
            { "name": "special_instructions", "type": "files", "description": "Any special instructions regarding the migration" }
          ]
        },
        {
          "ticket_type": "SFTP New Connectivity",
          "description": "To establish SFTP connectivity between Marlette and external vendors.",
          "fields": [
            { "name": "email", "type": "string", "description": "" },
            { "name": "summary", "type": "string", "description": "" },
            { "name": "scope_of_work", "type": "string", "description": "Detailed explanation of the work to be done" },
            { "name": "investor_name", "type": "string", "description": "The unique identifier or name of the investor for whom the SFTP connection is being established." },
            { "name": "sftp_server_address", "type": "string", "description": "The URL or IP address of the investor's SFTP server." },
            { "name": "authentication_type", "type": "choice", "options": AUTHENTICATION_TYPES, "description": "Specify the authentication method to be used" },
            { "name": "username", "type": "string", "description": "Username required for SFTP access" },
            { "name": "password", "type": "string", "description": "The password associated with the username" },
            { "name": "encryption_method", "type": "choice", "options": ENCRYPTION_METHODS, "description": "Specify encryption method used" },
            {
              "name": "sftp_type",
              "type": "choice",
              "options": SFTP_TYPES,
              "description": "Select the type of SFTP connection being requested or configured."
            },
            { "name": "port_number", "type": "string", "description": "The port number used to connect to the SFTP server" },
            { "name": "directory_path", "type": "string", "description": "The specific directory path on  the SFTP server where files should be uploaded/downloaded." },
            { "name": "ssh_key", "type": "file", "description": "Upload the SSH key file if SSH key authentication is being used" },
            { "name": "encryption_key", "type": "file", "description": "Upload the encryption key if one is available for secure communication" },
            { "name": "database", "type": "string", "description": "Databse name if applicable" },
            { "name": "notification_email", "type": "string", "description": "Email address where notifications about the connection status should be sent" },
            { "name": "additional_information", "type": "string", "description": "Any additional details regarding the request" }
          ]
        },
        {
          "ticket_type": "XMatters consultation request",
          "description": "For requesting assistance with an on-call schedule or workflows in XMatters. Also for onboarding a new team to Xmatters for off-hours notifications and communications.",
          "fields": [
            { "name": "email", "type": "string", "description": "" },
            { "name": "summary", "type": "string", "description": "" },
            { "name": "xmatters_questions", "type": "rich_text", "description": "Here's what I need to know about Xmatters?" },
            { "name": "on_call_questions", "type": "rich_text", "description": "How does XMatters work with my on-call schedule?" },
            { "name": "workflow_questions", "type": "rich_text", "description": "How does XMatters work with my workflow(s)?" },
            { "name": "support_questions", "type": "rich_text", "description": "How can we best support you? Feel free to add any additonal details, question, or comments." }
            { "name": "proposed_meeting_date", "type": "date", "description": "Provide a proposed meeting date" },
            { "name": "proposed_meeting_time", "type": "time", "description": "Provide a proposed meeting time" },
          ]
        }
      ],
      "Report an Incident": [
        {
          "ticket_type": "Open an incident here",
          "description": "Let us know if something isn't working properly and we'll aim to get it back up and running",
          "fields": [
            { "name": "email", "type": "string", "description": "" },
            { "name": "summary", "type": "string", "description": "A brief descriptive title that summarizes this issue (Max 75 chars)" },
            { "name": "description", "type": "string", "description": "A detailed description of the problem, indcluding any error messages or unusual behavior." },
            {
              "name": "urgency",
              "type": "choice",
              "options": URGENCY_LEVELS,
              "description": "The urgency level of the issue, indicating its severity asd impact on operations. Repsponse Turnaround - Critical: 0-2 Hours, High: 4 Hours, Medium: 24 Hours, Low 48 Hours"
            },
            { "name": "attachments", "type": "files", "description": "Attach any screenshots or supporting documents" }
          ]
        }
      ]
    }
  }
}
