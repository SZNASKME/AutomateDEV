from client.uc.resources import Calendar, EmailConnection, Script, Task, Trigger

FETCH_BUNDLE_DEFINITION_RESPONSE = [
    Task(
        endpoint="resources/task",
        name="Sleep 0",
        subtype="timer",
        definition={
            "addedBy": "ops.admin",
            "description": "Sleep for 0 seconds.",
            "name": "Sleep 0",
            "type": "Timer",
        },
        filters={},
        description=None,
    )
]

FETCH_WORKFLOW_DEFINITION_RESPONSE = [
    Task(
        endpoint="resources/task",
        name="Sleep 0",
        subtype="timer",
        definition={
            "addedBy": "*",
            "description": "Sleep for 0 seconds.",
            "name": "Sleep 0",
            "type": "Timer",
        },
        filters={},
        description=None,
    ),
]

FETCH_DEFINITION_BY_NAME_RESPONSE = [
    Task(
        endpoint="resources/task",
        name="Sleep 60",
        subtype="sleep",
        definition={
            "type": "taskSleep",
            "actions": {
                "abortActions": [],
                "emailNotifications": [],
                "setVariableActions": [],
                "snmpNotifications": [],
                "systemOperations": [],
            },
        },
        filters={},
        description=None,
    ),
    Task(
        endpoint="resources/task",
        name="Sleep 30",
        subtype="sleep",
        definition={
            "type": "taskSleep",
            "actions": {
                "abortActions": [],
                "emailNotifications": [],
                "setVariableActions": [],
                "snmpNotifications": [],
                "systemOperations": [],
            },
        },
        filters={},
        description=None,
    ),
]


FETCH_ALL_UC_DEFINITIONS = [
    Task(
        endpoint="resources/task",
        name="test-task",
        subtype="sleep",
        definition={
            "type": "test-task",
            "actions": {
                "abortActions": [],
                "emailNotifications": [],
                "setVariableActions": [],
                "snmpNotifications": [],
                "systemOperations": [],
            },
        },
        filters={},
        description=None,
    ),
    Trigger(
        endpoint="resources/trigger",
        name="test-trigger",
        subtype="sleep",
        definition={
            "type": "trigger",
            "actions": {
                "abortActions": [],
                "emailNotifications": [],
                "setVariableActions": [],
                "snmpNotifications": [],
                "systemOperations": [],
            },
        },
        filters={},
    ),
    Calendar(
        endpoint="resources/calendar",
        name="test-calendar",
        subtype="None",
        definition={
            "type": "calendar",
            "actions": {
                "abortActions": [],
                "emailNotifications": [],
                "setVariableActions": [],
                "snmpNotifications": [],
                "systemOperations": [],
            },
        },
        filters={},
    ),
    Script(
        endpoint="resources/script",
        name="test-script",
        subtype=None,
        definition={
            "type": "script",
            "actions": {
                "abortActions": [],
                "emailNotifications": [],
                "setVariableActions": [],
                "snmpNotifications": [],
                "systemOperations": [],
            },
        },
        filters={},
    ),
]

FULL_TASK_DEFINITION = [
    Task(
        endpoint="resources/task",
        name="test-task",
        subtype="Timer",
        definition={
            "type": "test-task",
            "actions": {
                "abortActions": [],
                "emailNotifications": [],
                "setVariableActions": [],
                "snmpNotifications": [],
                "systemOperations": [],
            },
            "subtype": "taskSleep",
        },
        filters={},
        description=None,
    ),
]

EXPORTED_GIT_DEFINITIONS = []

for git_definition in FETCH_ALL_UC_DEFINITIONS:
    EXPORTED_GIT_DEFINITIONS.append((git_definition, "git_path", "error_description"))


universal_task = Task(
    endpoint="resources/task",
    name="test-universal-task",
    subtype="Universal",
    definition={
        "type": "test-task",
        "template": "Test Integration",
        "actions": {
            "abortActions": [],
            "emailNotifications": [],
            "setVariableActions": [],
            "snmpNotifications": [],
            "systemOperations": [],
        },
    },
    filters={},
    description=None,
)

connection_task = EmailConnection(
    endpoint="resources/connection",
    name="test-email-connection",
    subtype="emailconnection",
    definition={
        "type": "test-connection",
        "actions": {
            "abortActions": [],
            "emailNotifications": [],
            "setVariableActions": [],
            "snmpNotifications": [],
            "systemOperations": [],
        },
    },
    filters={},
)


INPUT = {
    "uc_url": "http://example_uc.com/",
    "selection_method": ["bundle"],
    "uc_ssl_cert_verification": True,
    "git_commit_message": "commit message",
    "uc_credentials": {
        "password": "uc_password",
        "token": "",
        "user": "uc_user",
        "keyLocation": "",
        "pasphrase": "",
    },
    "uc_credentials.password": "admin",
    "git_repository_branch": ["branch1"],
    "proxy_ca_bundle_file": "",
    "git_ssl_cert_verification": True,
    "git_repository_path": "path/",
    "git_credentials": {
        "password": "",
        "token": "git_example_token",
        "user": "user",
        "keyLocation": "",
        "pasphrase": "",
    },
    "git_credentials.password": "",
    "uc_credentials.token": "",
    "uc_credentials.user": "uc_user",
    "add_uc_definitions_list": "",
    "proxy_type": ["-- None --"],
    "modify_uc_definitions_list": "",
    "git_service_provider_url": "https://gitlab.com/",
    "git_credentials.token": "git_example_token",
    "uc_credentials.keyLocation": "",
    "git_credentials.user": "user",
    "proxy": "",
    "selection_name": ["Example"],
    "remove_uc_definitions_list": "",
    "git_credentials.keyLocation": "",
    "action": ["Export to Git Repository"],
    "git_repository": ["example/repo"],
    "uc_credentials.pasphrase": "",
    "git_service_provider": ["GitLab"],
    "git_repository_file_format": ["Yaml"],
    "selection_exclude_list": [],
    "git_credentials.pasphrase": "",
}

BITBUCKET_COMPARE_TWO_COMMITS_RESPONSE = {
    "values": [
        {
            "status": "modified",
            "old": {
                "path": "import/Scripts/Data/slack-bot-acl-all-access.json",
                "type": "commit_file",
                "escaped_path": "import/Scripts/Data/slack-bot-acl-all-access.json",
                "links": {},
            },
            "new": {
                "path": "import/Scripts/Data/slack-bot-acl-all-access.json",
                "type": "commit_file",
                "escaped_path": "import/Scripts/Data/slack-bot-acl-all-access.json",
                "links": {},
            },
        },
        {
            "status": "modified",
            "old": {
                "path": "test.txt",
                "type": "commit_file",
                "escaped_path": "test.txt",
                "links": {},
            },
            "new": {
                "path": "test_changed.txt",
                "type": "commit_file",
                "escaped_path": "test_changed.txt",
                "links": {},
            },
        },
        {
            "status": "removed",
            "old": {
                "path": "import/removed_test1.py",
                "type": "commit_file",
                "escaped_path": "import/removed_test1.py",
                "links": {},
            },
            "new": None,
        },
        {
            "status": "removed",
            "old": {
                "path": "removed_test2.py",
                "type": "commit_file",
                "escaped_path": "removed_test2.py",
                "links": {},
            },
            "new": None,
        },
        {
            "status": "added",
            "old": None,
            "new": {
                "path": "import/added_test1.txt",
                "type": "commit_directory",
                "escaped_path": "import/added_test1.txt",
                "links": {},
            },
        },
    ]
}

ALL_BITBUCKET_AFFECTED_FILES = {
    "modified": [
        "import/Scripts/Data/slack-bot-acl-all-access.json",
        "test_changed.txt",
    ],
    "added": [],
    "removed": ["import/removed_test1.py", "removed_test2.py"],
}

WEBHOOK_PAYLOAD = {
    "push": {
        "changes": [
            {
                "old": {
                    "name": "test_branch",
                    "target": {
                        "type": "commit",
                        "hash": "30f873b51f4b0a5d4c4bb3e0095684c0c82643d1",
                        "date": "2023-10-23T16:27:39+00:00",
                        "author": {
                            "type": "author",
                            "raw": "universal-extensions <universal.extensions@stonebranch.com>",
                            "user": {
                                "display_name": "universal-extensions",
                                "links": {
                                    "self": {
                                        "href": "https://api.bitbucket.org/2.0/users/%7B4fb1d0da-61ea-4257-b0f0-74e13663002c%7D"
                                    },
                                    "avatar": {
                                        "href": "https://secure.gravatar.com/avatar/ae0ad1debf08f74fc0799330520ffad2?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FU-6.png"
                                    },
                                    "html": {
                                        "href": "https://bitbucket.org/%7B4fb1d0da-61ea-4257-b0f0-74e13663002c%7D/"
                                    },
                                },
                                "type": "user",
                                "uuid": "{4fb1d0da-61ea-4257-b0f0-74e13663002c}",
                                "account_id": "641467307222b08f3e718585",
                                "nickname": "universal-extensions",
                            },
                        },
                        "message": "slack-bot-acl-all-access.json edited online with Bitbucket",
                        "summary": {
                            "type": "rendered",
                            "raw": "slack-bot-acl-all-access.json edited online with Bitbucket",
                            "markup": "markdown",
                            "html": "<p>slack-bot-acl-all-access.json edited online with Bitbucket</p>",
                        },
                        "links": {
                            "self": {
                                "href": "https://api.bitbucket.org/2.0/repositories/jobascode/test_repo_ue_jobs_as_code/commit/30f873b51f4b0a5d4c4bb3e0095684c0c82643d1"
                            },
                            "html": {
                                "href": "https://bitbucket.org/jobascode/test_repo_ue_jobs_as_code/commits/30f873b51f4b0a5d4c4bb3e0095684c0c82643d1"
                            },
                        },
                        "parents": [
                            {
                                "hash": "49be7010e9c9266ed7f841e9c4e75eb45998b558",
                                "links": {
                                    "self": {
                                        "href": "https://api.bitbucket.org/2.0/repositories/jobascode/test_repo_ue_jobs_as_code/commit/49be7010e9c9266ed7f841e9c4e75eb45998b558"
                                    },
                                    "html": {
                                        "href": "https://bitbucket.org/jobascode/test_repo_ue_jobs_as_code/commits/49be7010e9c9266ed7f841e9c4e75eb45998b558"
                                    },
                                },
                                "type": "commit",
                            }
                        ],
                        "rendered": {},
                        "properties": {},
                    },
                    "links": {
                        "self": {
                            "href": "https://api.bitbucket.org/2.0/repositories/jobascode/test_repo_ue_jobs_as_code/refs/branches/test_branch"
                        },
                        "commits": {
                            "href": "https://api.bitbucket.org/2.0/repositories/jobascode/test_repo_ue_jobs_as_code/commits/test_branch"
                        },
                        "html": {
                            "href": "https://bitbucket.org/jobascode/test_repo_ue_jobs_as_code/branch/test_branch"
                        },
                    },
                    "type": "branch",
                    "merge_strategies": ["merge_commit", "squash", "fast_forward"],
                    "default_merge_strategy": "merge_commit",
                },
                "new": {
                    "name": "test_branch",
                    "target": {
                        "type": "commit",
                        "hash": "47ec2a346d7a5b44bac940dfd04ed83a7ac46442",
                        "date": "2023-10-23T16:44:22+00:00",
                        "author": {
                            "type": "author",
                            "raw": "ioanna.tsintzou <ioanna.tsintzou@stonebranch.com>",
                        },
                        "message": "trigger my webhook with this commit\n",
                        "summary": {
                            "type": "rendered",
                            "raw": "trigger my webhook with this commit\n",
                            "markup": "markdown",
                            "html": "<p>trigger my webhook with this commit</p>",
                        },
                        "links": {
                            "self": {
                                "href": "https://api.bitbucket.org/2.0/repositories/jobascode/test_repo_ue_jobs_as_code/commit/47ec2a346d7a5b44bac940dfd04ed83a7ac46442"
                            },
                            "html": {
                                "href": "https://bitbucket.org/jobascode/test_repo_ue_jobs_as_code/commits/47ec2a346d7a5b44bac940dfd04ed83a7ac46442"
                            },
                        },
                        "parents": [
                            {
                                "hash": "30f873b51f4b0a5d4c4bb3e0095684c0c82643d1",
                                "links": {
                                    "self": {
                                        "href": "https://api.bitbucket.org/2.0/repositories/jobascode/test_repo_ue_jobs_as_code/commit/30f873b51f4b0a5d4c4bb3e0095684c0c82643d1"
                                    },
                                    "html": {
                                        "href": "https://bitbucket.org/jobascode/test_repo_ue_jobs_as_code/commits/30f873b51f4b0a5d4c4bb3e0095684c0c82643d1"
                                    },
                                },
                                "type": "commit",
                            }
                        ],
                        "rendered": {},
                        "properties": {},
                    },
                    "links": {
                        "self": {
                            "href": "https://api.bitbucket.org/2.0/repositories/jobascode/test_repo_ue_jobs_as_code/refs/branches/test_branch"
                        },
                        "commits": {
                            "href": "https://api.bitbucket.org/2.0/repositories/jobascode/test_repo_ue_jobs_as_code/commits/test_branch"
                        },
                        "html": {
                            "href": "https://bitbucket.org/jobascode/test_repo_ue_jobs_as_code/branch/test_branch"
                        },
                    },
                    "type": "branch",
                    "merge_strategies": ["merge_commit", "squash", "fast_forward"],
                    "default_merge_strategy": "merge_commit",
                },
                "truncated": False,
                "created": False,
                "forced": False,
                "closed": False,
                "links": {
                    "commits": {
                        "href": "https://api.bitbucket.org/2.0/repositories/jobascode/test_repo_ue_jobs_as_code/commits?include=47ec2a346d7a5b44bac940dfd04ed83a7ac46442&exclude=30f873b51f4b0a5d4c4bb3e0095684c0c82643d1"
                    },
                    "diff": {
                        "href": "https://api.bitbucket.org/2.0/repositories/jobascode/test_repo_ue_jobs_as_code/diff/47ec2a346d7a5b44bac940dfd04ed83a7ac46442..30f873b51f4b0a5d4c4bb3e0095684c0c82643d1"
                    },
                    "html": {
                        "href": "https://bitbucket.org/jobascode/test_repo_ue_jobs_as_code/branches/compare/47ec2a346d7a5b44bac940dfd04ed83a7ac46442..30f873b51f4b0a5d4c4bb3e0095684c0c82643d1"
                    },
                },
                "commits": [
                    {
                        "type": "commit",
                        "hash": "47ec2a346d7a5b44bac940dfd04ed83a7ac46442",
                        "date": "2023-10-23T16:44:22+00:00",
                        "author": {
                            "type": "author",
                            "raw": "ioanna.tsintzou <ioanna.tsintzou@stonebranch.com>",
                        },
                        "message": "trigger my webhook with this commit\n",
                        "summary": {
                            "type": "rendered",
                            "raw": "trigger my webhook with this commit\n",
                            "markup": "markdown",
                            "html": "<p>trigger my webhook with this commit</p>",
                        },
                        "links": {
                            "self": {
                                "href": "https://api.bitbucket.org/2.0/repositories/jobascode/test_repo_ue_jobs_as_code/commit/47ec2a346d7a5b44bac940dfd04ed83a7ac46442"
                            },
                            "html": {
                                "href": "https://bitbucket.org/jobascode/test_repo_ue_jobs_as_code/commits/47ec2a346d7a5b44bac940dfd04ed83a7ac46442"
                            },
                            "diff": {
                                "href": "https://api.bitbucket.org/2.0/repositories/jobascode/test_repo_ue_jobs_as_code/diff/47ec2a346d7a5b44bac940dfd04ed83a7ac46442"
                            },
                            "approve": {
                                "href": "https://api.bitbucket.org/2.0/repositories/jobascode/test_repo_ue_jobs_as_code/commit/47ec2a346d7a5b44bac940dfd04ed83a7ac46442/approve"
                            },
                            "comments": {
                                "href": "https://api.bitbucket.org/2.0/repositories/jobascode/test_repo_ue_jobs_as_code/commit/47ec2a346d7a5b44bac940dfd04ed83a7ac46442/comments"
                            },
                            "statuses": {
                                "href": "https://api.bitbucket.org/2.0/repositories/jobascode/test_repo_ue_jobs_as_code/commit/47ec2a346d7a5b44bac940dfd04ed83a7ac46442/statuses"
                            },
                            "patch": {
                                "href": "https://api.bitbucket.org/2.0/repositories/jobascode/test_repo_ue_jobs_as_code/patch/47ec2a346d7a5b44bac940dfd04ed83a7ac46442"
                            },
                        },
                        "parents": [
                            {
                                "hash": "30f873b51f4b0a5d4c4bb3e0095684c0c82643d1",
                                "links": {
                                    "self": {
                                        "href": "https://api.bitbucket.org/2.0/repositories/jobascode/test_repo_ue_jobs_as_code/commit/30f873b51f4b0a5d4c4bb3e0095684c0c82643d1"
                                    },
                                    "html": {
                                        "href": "https://bitbucket.org/jobascode/test_repo_ue_jobs_as_code/commits/30f873b51f4b0a5d4c4bb3e0095684c0c82643d1"
                                    },
                                },
                                "type": "commit",
                            }
                        ],
                        "rendered": {},
                        "properties": {},
                    }
                ],
            }
        ]
    },
    "repository": {
        "type": "repository",
        "full_name": "jobascode/test_repo_ue_jobs_as_code",
        "links": {
            "self": {
                "href": "https://api.bitbucket.org/2.0/repositories/jobascode/test_repo_ue_jobs_as_code"
            },
            "html": {
                "href": "https://bitbucket.org/jobascode/test_repo_ue_jobs_as_code"
            },
            "avatar": {
                "href": "https://bytebucket.org/ravatar/%7B1fca0c23-1ed5-4b95-9914-6f587b3ae855%7D?ts=default"
            },
        },
        "name": "test_repo_ue_jobs_as_code",
        "scm": "git",
        "website": None,
        "owner": {
            "display_name": "jobascode",
            "links": {
                "self": {
                    "href": "https://api.bitbucket.org/2.0/workspaces/%7Bde160199-747b-49c5-9c6f-1845d577432d%7D"
                },
                "avatar": {"href": "https://bitbucket.org/account/jobascode/avatar/"},
                "html": {
                    "href": "https://bitbucket.org/%7Bde160199-747b-49c5-9c6f-1845d577432d%7D/"
                },
            },
            "type": "team",
            "uuid": "{de160199-747b-49c5-9c6f-1845d577432d}",
            "username": "jobascode",
        },
        "workspace": {
            "type": "workspace",
            "uuid": "{de160199-747b-49c5-9c6f-1845d577432d}",
            "name": "jobascode",
            "slug": "jobascode",
            "links": {
                "avatar": {
                    "href": "https://bitbucket.org/workspaces/jobascode/avatar/?ts=1679059058"
                },
                "html": {"href": "https://bitbucket.org/jobascode/"},
                "self": {"href": "https://api.bitbucket.org/2.0/workspaces/jobascode"},
            },
        },
        "is_private": True,
        "project": {
            "type": "project",
            "key": "PROJ",
            "uuid": "{733abb79-b9ef-404d-a841-61172ab6f379}",
            "name": "project_jobascode",
            "links": {
                "self": {
                    "href": "https://api.bitbucket.org/2.0/workspaces/jobascode/projects/PROJ"
                },
                "html": {
                    "href": "https://bitbucket.org/jobascode/workspace/projects/PROJ"
                },
                "avatar": {
                    "href": "https://bitbucket.org/account/user/jobascode/projects/PROJ/avatar/32?ts=1679059551"
                },
            },
        },
        "uuid": "{1fca0c23-1ed5-4b95-9914-6f587b3ae855}",
        "parent": None,
    },
    "actor": {
        "display_name": "universal-extensions",
        "links": {
            "self": {
                "href": "https://api.bitbucket.org/2.0/users/%7B4fb1d0da-61ea-4257-b0f0-74e13663002c%7D"
            },
            "avatar": {
                "href": "https://secure.gravatar.com/avatar/ae0ad1debf08f74fc0799330520ffad2?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FU-6.png"
            },
            "html": {
                "href": "https://bitbucket.org/%7B4fb1d0da-61ea-4257-b0f0-74e13663002c%7D/"
            },
        },
        "type": "user",
        "uuid": "{4fb1d0da-61ea-4257-b0f0-74e13663002c}",
        "account_id": "641467307222b08f3e718585",
        "nickname": "universal-extensions",
    },
}


AZURE_DEVOPS_WEBHOOK = {
    "subscriptionId": "e6e4ef69-f88e-49c3-ab53-d32c5cab4c04",
    "notificationId": 23,
    "id": "c94d8aa8-e6b7-4290-b699-27bc88b7dae6",
    "eventType": "git.push",
    "publisherId": "tfs",
    "message": {
        "text": "Giorgos Skouras pushed updates to test-jac:main\r\n(https://dev.azure.com/giorgosskouras/test-jac/_git/test-jac/#version=GBmain)",
        "html": 'Giorgos Skouras pushed updates to <a href="https://dev.azure.com/giorgosskouras/test-jac/_git/test-jac/">test-jac</a>:<a href="https://dev.azure.com/giorgosskouras/test-jac/_git/test-jac/#version=GBmain">main</a>',
        "markdown": "Giorgos Skouras pushed updates to [test-jac](https://dev.azure.com/giorgosskouras/test-jac/_git/test-jac/):[main](https://dev.azure.com/giorgosskouras/test-jac/_git/test-jac/#version=GBmain)",
    },
    "detailedMessage": {
        "text": "Giorgos Skouras pushed a commit to test-jac:main\r\n - delete a6a6a21d (https://dev.azure.com/giorgosskouras/test-jac/_git/test-jac/commit/a6a6a21d05822136327e75d134005c7044335119)",
        "html": 'Giorgos Skouras pushed a commit to <a href="https://dev.azure.com/giorgosskouras/test-jac/_git/test-jac/">test-jac</a>:<a href="https://dev.azure.com/giorgosskouras/test-jac/_git/test-jac/#version=GBmain">main</a>\r\n<ul>\r\n<li>delete <a href="https://dev.azure.com/giorgosskouras/test-jac/_git/test-jac/commit/a6a6a21d05822136327e75d134005c7044335119">a6a6a21d</a></li>\r\n</ul>',
        "markdown": "Giorgos Skouras pushed a commit to [test-jac](https://dev.azure.com/giorgosskouras/test-jac/_git/test-jac/):[main](https://dev.azure.com/giorgosskouras/test-jac/_git/test-jac/#version=GBmain)\r\n* delete [a6a6a21d](https://dev.azure.com/giorgosskouras/test-jac/_git/test-jac/commit/a6a6a21d05822136327e75d134005c7044335119)",
    },
    "resource": {
        "commits": [
            {
                "commitId": "a6a6a21d05822136327e75d134005c7044335119",
                "author": {
                    "name": "Giorgos Skouras",
                    "email": "giorgos.skouras@stonebranch.com",
                    "date": "2023-11-09T15:46:29Z",
                },
                "committer": {
                    "name": "Giorgos Skouras",
                    "email": "giorgos.skouras@stonebranch.com",
                    "date": "2023-11-09T15:46:29Z",
                },
                "comment": "delete",
                "url": "https://dev.azure.com/giorgosskouras/_apis/git/repositories/4c722009-b4d6-4a2c-93d7-7498b722b014/commits/a6a6a21d05822136327e75d134005c7044335119",
            }
        ],
        "refUpdates": [
            {
                "name": "refs/heads/main",
                "oldObjectId": "c7a10fdb4c550e81c58a28d441b93639dca5444b",
                "newObjectId": "a6a6a21d05822136327e75d134005c7044335119",
            }
        ],
        "repository": {
            "id": "4c722009-b4d6-4a2c-93d7-7498b722b014",
            "name": "test-jac",
            "url": "https://dev.azure.com/giorgosskouras/_apis/git/repositories/4c722009-b4d6-4a2c-93d7-7498b722b014",
            "project": {
                "id": "0e651723-4265-4bee-9ef1-602e58c16ddc",
                "name": "test-jac",
                "url": "https://dev.azure.com/giorgosskouras/_apis/projects/0e651723-4265-4bee-9ef1-602e58c16ddc",
                "state": "wellFormed",
                "visibility": "unchanged",
                "lastUpdateTime": "0001-01-01T00:00:00",
            },
            "defaultBranch": "refs/heads/main",
            "remoteUrl": "https://dev.azure.com/giorgosskouras/test-jac/_git/test-jac",
        },
        "pushedBy": {
            "displayName": "Giorgos Skouras",
            "url": "https://spsprodneu1.vssps.visualstudio.com/A4af4333f-25bd-4dcd-88e8-6f597f8f1e23/_apis/Identities/e7a1af45-b36d-6f00-8bb2-b46b4a3475b8",
            "_links": {
                "avatar": {
                    "href": "https://dev.azure.com/giorgosskouras/_apis/GraphProfile/MemberAvatars/aad.ZTdhMWFmNDUtYjM2ZC03ZjAwLThiYjItYjQ2YjRhMzQ3NWI4"
                }
            },
            "id": "e7a1af45-b36d-6f00-8bb2-b46b4a3475b8",
            "uniqueName": "giorgos.skouras@stonebranch.com",
            "imageUrl": "https://dev.azure.com/giorgosskouras/_api/_common/identityImage?id=e7a1af45-b36d-6f00-8bb2-b46b4a3475b8",
            "descriptor": "aad.ZTdhMWFmNDUtYjM2ZC03ZjAwLThiYjItYjQ2YjRhMzQ3NWI4",
        },
        "pushId": 20,
        "date": "2023-11-09T15:46:29.1993202Z",
        "url": "https://dev.azure.com/giorgosskouras/_apis/git/repositories/4c722009-b4d6-4a2c-93d7-7498b722b014/pushes/20",
        "_links": {
            "self": {
                "href": "https://dev.azure.com/giorgosskouras/_apis/git/repositories/4c722009-b4d6-4a2c-93d7-7498b722b014/pushes/20"
            },
            "repository": {
                "href": "https://dev.azure.com/giorgosskouras/0e651723-4265-4bee-9ef1-602e58c16ddc/_apis/git/repositories/4c722009-b4d6-4a2c-93d7-7498b722b014"
            },
            "commits": {
                "href": "https://dev.azure.com/giorgosskouras/_apis/git/repositories/4c722009-b4d6-4a2c-93d7-7498b722b014/pushes/20/commits"
            },
            "pusher": {
                "href": "https://spsprodneu1.vssps.visualstudio.com/A4af4333f-25bd-4dcd-88e8-6f597f8f1e23/_apis/Identities/e7a1af45-b36d-6f00-8bb2-b46b4a3475b8"
            },
            "refs": {
                "href": "https://dev.azure.com/giorgosskouras/0e651723-4265-4bee-9ef1-602e58c16ddc/_apis/git/repositories/4c722009-b4d6-4a2c-93d7-7498b722b014/refs/heads/main"
            },
        },
    },
    "resourceVersion": "1.0",
    "resourceContainers": {
        "collection": {
            "id": "9548d1ba-c48b-4ec1-bba2-63eaef0d57a8",
            "baseUrl": "https://dev.azure.com/giorgosskouras/",
        },
        "account": {
            "id": "4af4333f-25bd-4dcd-88e8-6f597f8f1e23",
            "baseUrl": "https://dev.azure.com/giorgosskouras/",
        },
        "project": {
            "id": "0e651723-4265-4bee-9ef1-602e58c16ddc",
            "baseUrl": "https://dev.azure.com/giorgosskouras/",
        },
    },
    "createdDate": "2023-11-09T15:46:35.8343173Z",
}
