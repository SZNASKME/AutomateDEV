from client.uc.resources import CustomDay, DbConnection, Script, Task, Workflow

ADD_UC_DEFINITIONS_LIST = "Scripts/ops_script_0df65ecfb68a48b0875c53765abeea5f.json, Connections/Database Connections/ops_database_connection_21007e34d7d24ef796e559388baa8d71.json"

EVALUATED_ADD_UC_DEFINITIONS_LIST = [
    "Scripts/ops_script_0df65ecfb68a48b0875c53765abeea5f.json",
    "Connections/Database Connections/ops_database_connection_21007e34d7d24ef796e559388baa8d71.json",
]

IMPORT_SCRIPT = Script(
    endpoint="resources/script",
    name="jobs-as-code-scripts",
    subtype=None,
    definition={
        "content": '#!/usr/bin/sh\n\necho "${jobs_as_code_global_var}"',
        "description": None,
        "exportReleaseLevel": "7.3.0.0",
        "exportTable": "ops_script",
        "notes": [],
        "opswiseGroups": ["jobs-as-code"],
        "resolveVariables": True,
        "retainSysIds": True,
        "scriptName": "jobs-as-code-scripts",
        "scriptType": "Data",
        "sysId": "0df65ecfb68a48b0875c53765abeea5f",
        "version": 1,
    },
    filters={},
)

IMPORT_DBCONNECTION = DbConnection(
    endpoint="resources/databaseconnection",
    name="jobs-as-code-db-connection",
    subtype=None,
    definition={
        "credentials": None,
        "dbDescription": None,
        "dbDriver": "com.mysql.cj.jdbc.Driver",
        "dbMaxRows": 100,
        "dbType": "MySQL",
        "dbUrl": "jdbc:mysql://<server>:<port3306>/<database>",
        "exportReleaseLevel": "7.3.0.0",
        "exportTable": "ops_database_connection",
        "name": "jobs-as-code-db-connection",
        "opswiseGroups": ["jobs-as-code"],
        "retainSysIds": True,
        "sysId": "21007e34d7d24ef796e559388baa8d71",
        "version": 3,
    },
    filters={},
)

UPDATE_UC_DEFINITIONS_LIST = (
    "Custom Days/ops_custom_day_3bedcc85a6fa47e5a02665f6d0ced830.json"
)

EVALUATED_UPDATE_UC_DEFINITIONS_LIST = [
    "import/Custom Days/ops_custom_day_3bedcc85a6fa47e5a02665f6d0ced830.json",
]

IMPORT_CUSTOMDAY = CustomDay(
    endpoint="resources/customday",
    name="Xmas",
    subtype=None,
    definition={
        "adjustment": "None",
        "adjustmentAmount": 1,
        "adjustmentType": "Day",
        "category": "Holiday",
        "comments": None,
        "ctype": "Absolute Repeating Date",
        "date": None,
        "dateList": [],
        "day": 25,
        "dayofweek": "Sun",
        "exportReleaseLevel": "7.3.0.0",
        "exportTable": "ops_custom_day",
        "holiday": True,
        "month": "Dec",
        "name": "Xmas",
        "nthAmount": 1,
        "nthType": "Day",
        "observedRules": [],
        "period": False,
        "relfreq": "1st",
        "retainSysIds": True,
        "sysId": "3bedcc85a6fa47e5a02665f6d0ced830",
        "version": 1,
    },
    filters={},
)

REMOVE_UC_DEFINITIONS_LIST = "task/ops_task_workflow_3850c1a8bb824320b8113a0cf5a81e47.json, task/ops_task_ftp_212e6668bd354b83af1e761f3ed9b4ef.json"

EVALUATED_REMOVE_UC_DEFINITIONS_LIST = [
    "import/task/ops_task_workflow_3850c1a8bb824320b8113a0cf5a81e47.json",
    "import/task/ops_task_ftp_212e6668bd354b83af1e761f3ed9b4ef.json",
]

IMPORT_TASK = Task(
    endpoint="resources/task",
    name="jobs-as-code-ft-task",
    subtype="ftp",
    definition={"dummy": "this definitions is not verified"},
    filters={},
)

IMPORT_WORKFLOW = Workflow(
    endpoint="resources/task",
    name="jobs-as-code-wf",
    subtype="workflow",
    definition={"dummy": "this definitions is not verified"},
    filters={},
)


definitions_base_counter = {
    "agentcluster": 0,
    "businessservice": 0,
    "bundle": 0,
    "calendar": 0,
    "databaseconnection": 0,
    "emailconnection": 0,
    "peoplesoftconnection": 0,
    "sapconnection": 0,
    "snmpmanager": 0,
    "customday": 0,
    "emailtemplate": 0,
    "script": 0,
    "task": 0,
    "trigger": 0,
    "variable": 0,
    "virtualresource": 0,
}

definitions_selected = {
    "agentcluster": 0,
    "businessservice": 0,
    "bundle": 0,
    "calendar": 0,
    "databaseconnection": 1,
    "emailconnection": 0,
    "peoplesoftconnection": 0,
    "sapconnection": 0,
    "snmpmanager": 0,
    "customday": 1,
    "emailtemplate": 0,
    "script": 1,
    "task": 2,
    "trigger": 0,
    "variable": 0,
    "virtualresource": 0,
}

definitions_created = {
    "agentcluster": 0,
    "businessservice": 0,
    "bundle": 0,
    "calendar": 0,
    "databaseconnection": 1,
    "emailconnection": 0,
    "peoplesoftconnection": 0,
    "sapconnection": 0,
    "snmpmanager": 0,
    "customday": 0,
    "emailtemplate": 0,
    "script": 1,
    "task": 0,
    "trigger": 0,
    "variable": 0,
    "virtualresource": 0,
}

definitions_updated = {
    "agentcluster": 0,
    "businessservice": 0,
    "bundle": 0,
    "calendar": 0,
    "databaseconnection": 0,
    "emailconnection": 0,
    "peoplesoftconnection": 0,
    "sapconnection": 0,
    "snmpmanager": 0,
    "customday": 1,
    "emailtemplate": 0,
    "script": 0,
    "task": 0,
    "trigger": 0,
    "variable": 0,
    "virtualresource": 0,
}

definitions_deleted = {
    "agentcluster": 0,
    "businessservice": 0,
    "bundle": 0,
    "calendar": 0,
    "databaseconnection": 0,
    "emailconnection": 0,
    "peoplesoftconnection": 0,
    "sapconnection": 0,
    "snmpmanager": 0,
    "customday": 0,
    "emailtemplate": 0,
    "script": 0,
    "task": 2,
    "trigger": 0,
    "variable": 0,
    "virtualresource": 0,
}


GET_BRANCH_RESULT = [
    "import/Bundles/test_bundle.json",
    "import/Custom Days/test_custom_day_1.json",
    "import/Connections/Database Connection/test_dbconn.json",
    "import/Connections/Email Connection/test_emainconn.json",
    "import/Email Templates/test_email_template.json",
    "import/Tasks/Workflow/test_workflow.json",
    "import/Trigger/Time/test_trigger_time.json",
]


ALL_UC_GIT_ABSOLUTE_FILEPATHS = [
    "import/Bundles/test_bundle.json",
    "import/Custom Days/test_custom_day_1.json",
    "import/Connections/Database Connection/test_dbconn.json",
    "import/Connections/Email Connection/test_emainconn.json",
    "import/Email Templates/test_email_template.json",
    "import/Tasks/Workflow/test_workflow.json",
    "import/Trigger/Time/test_trigger_time.json",
]

JSON_GIT_CONTENT = """{
  "adjustment" : "None",
  "adjustmentAmount" : 1,
  "adjustmentType" : "Day",
  "category" : "Holiday",
  "comments" : null,
  "ctype" : "Absolute Repeating Date",
  "date" : null,
  "dateList" : [ ],
  "day" : 25,
  "dayofweek" : "Sun",
  "exportReleaseLevel" : "7.3.0.0",
  "exportTable" : "ops_custom_day",
  "holiday" : true,
  "month" : "Dec",
  "name" : "Xmas",
  "nthAmount" : 1,
  "nthType" : "Day",
  "observedRules" : [ ],
  "period" : false,
  "relfreq" : "1st",
  "retainSysIds" : true,
  "sysId" : "3bedcc85a6fa47e5a02665f6d0ced830",
  "version" : 1
}"""

YAML_GIT_CONTENT = """
credentials:
dbDescription:
dbDriver: com.mysql.cj.jdbc.Driver
dbMaxRows: 100
dbType: MySQL
dbUrl: jdbc:mysql://<server>:<port3306>/<database>
exportReleaseLevel: 7.3.0.0
exportTable: ops_database_connection
name: jobs-as-code-db-connection
opswiseGroups:
- jobs-as-code
retainSysIds: true
sysId: 21007e34d7d24ef796e559388baa8d71
version: 3
"""

CONVERTED_YAML_TO_JSON_CONTENT = """
{
  "credentials" : null,
  "dbDescription" : null,
  "dbDriver" : "com.mysql.cj.jdbc.Driver",
  "dbMaxRows" : 100,
  "dbType" : "MySQL",
  "dbUrl" : "jdbc:mysql://<server>:<port3306>/<database>",
  "exportReleaseLevel" : "7.3.0.0",
  "exportTable" : "ops_database_connection",
  "name" : "jobs-as-code-db-connection",
  "opswiseGroups" : [ "jobs-as-code" ],
  "retainSysIds" : true,
  "sysId" : "21007e34d7d24ef796e559388baa8d71",
  "version" : 3
}
"""

TRANSFORMED_GIT_CONTENT = {
    "adjustment": "None",
    "adjustmentAmount": 1,
    "adjustmentType": "Day",
    "category": "Holiday",
    "comments": None,
    "ctype": "Absolute Repeating Date",
    "date": None,
    "dateList": [],
    "day": 25,
    "dayofweek": "Sun",
    "exportTable": "ops_custom_day",
    "holiday": True,
    "month": "Dec",
    "name": "Xmas",
    "nthAmount": 1,
    "nthType": "Day",
    "observedRules": [],
    "period": False,
    "relfreq": "1st",
    "retainSysIds": True,
}
