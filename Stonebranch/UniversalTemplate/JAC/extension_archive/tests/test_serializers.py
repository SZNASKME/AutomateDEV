import json
import os
import unittest

from serializers.extension_input import ExtensionInputSerializer, replace_git_url

from .test_data import INPUT, WEBHOOK_PAYLOAD


class TestExtensionInputSerializer(unittest.TestCase):
    def test_create_extension_input_action(self):
        serializer = ExtensionInputSerializer(**INPUT)
        assert serializer.action == "Export to Git Repository"

    def test_create_extension_input_git_repository_file_format(self):
        serializer = ExtensionInputSerializer(**INPUT)
        assert serializer.git_repository_file_format == "yaml"

    def test_duplicate_uc_definitions_list(self):
        input = INPUT.copy()
        input["add_uc_definitions_list"] = "definition1.yaml, definition1.yaml"
        serializer = ExtensionInputSerializer(**input)
        self.assertListEqual(serializer.add_uc_definitions_list, ["definition1.yaml"])

    def test_create_extension_input_git_commit_message(self):
        serializer = ExtensionInputSerializer(**INPUT)

    def test_create_extension_input_uc_url(self):
        serializer = ExtensionInputSerializer(**INPUT)
        assert serializer.uc_url == "http://example_uc.com"

    def test_bitbucket_url(self):
        bitbucket_url = replace_git_url("https://bitbucket.org/", "BitBucket")
        self.assertEqual(bitbucket_url, "https://api.bitbucket.org")

        bitbucket_url = replace_git_url("https://bitbucket.org", "BitBucket")
        self.assertEqual(bitbucket_url, "https://api.bitbucket.org")

        bitbucket_url = replace_git_url("https://mydomain.bitbucket.org", "BitBucket")
        self.assertEqual(bitbucket_url, "https://api.bitbucket.org")

        bitbucket_url = replace_git_url("https://mydomain.org", "BitBucket")
        self.assertEqual(bitbucket_url, "https://api.bitbucket.org")

    def test_gitlab_url(self):
        gitlab_url = replace_git_url("https://mydomain.org", "GitLab")
        self.assertEqual(gitlab_url, "https://mydomain.org")

        gitlab_url = replace_git_url("https://gitlab.com", "GitLab")
        self.assertEqual(gitlab_url, "https://gitlab.com")

    def test_github_url(self):
        github_url = replace_git_url("https://github.com", "GitHub")
        self.assertEqual(github_url, "https://api.github.com")

        github_url = replace_git_url("https://domain.github.org", "GitHub")
        self.assertEqual(github_url, "https://domain.github.org/api/v3")

        github_url = replace_git_url("https://domain.github.org/api/v3", "GitHub")
        self.assertEqual(github_url, "https://domain.github.org/api/v3")

    def test_webhook_payload_gitlab_provide(self):
        webhook_payload_input = INPUT.copy()
        webhook_payload_input["git_service_provider"] = ["GitLab"]
        webhook_payload_input["webhook_payload"] = str(WEBHOOK_PAYLOAD)
        serialized_input = ExtensionInputSerializer(**webhook_payload_input)
        self.assertEqual(serialized_input.webhook_payload, None)

    def test_webhook_payload_valid_bitbucket_provider(self):
        webhook_payload_input = INPUT.copy()
        webhook_payload_json_str = json.dumps(WEBHOOK_PAYLOAD)
        webhook_payload_input["git_service_provider"] = ["BitBucket"]
        webhook_payload_input["webhook_payload"] = webhook_payload_json_str
        serialized_input = ExtensionInputSerializer(**webhook_payload_input)
        self.assertEqual(serialized_input.webhook_payload, WEBHOOK_PAYLOAD)

    def test_ff_disable_default_commit_prefix(self):
        os.environ["UE_FF_DISABLE_DEFAULT_COMMIT_PREFIX"] = "False"
        serializer = ExtensionInputSerializer(**INPUT)
        self.assertFalse(serializer.ff_commit_msg)
        del os.environ["UE_FF_DISABLE_DEFAULT_COMMIT_PREFIX"]

        os.environ["UE_FF_DISABLE_DEFAULT_COMMIT_PREFIX"] = "false"
        serializer = ExtensionInputSerializer(**INPUT)
        self.assertFalse(serializer.ff_commit_msg)
        del os.environ["UE_FF_DISABLE_DEFAULT_COMMIT_PREFIX"]

        os.environ["UE_FF_DISABLE_DEFAULT_COMMIT_PREFIX"] = "True"
        print(os.getenv("UE_FF_DISABLE_DEFAULT_COMMIT_PREFIX"))
        serializer = ExtensionInputSerializer(**INPUT)
        self.assertTrue(serializer.ff_commit_msg)
        del os.environ["UE_FF_DISABLE_DEFAULT_COMMIT_PREFIX"]

        os.environ["UE_FF_DISABLE_DEFAULT_COMMIT_PREFIX"] = "true"
        serializer = ExtensionInputSerializer(**INPUT)
        self.assertTrue(serializer.ff_commit_msg)
        del os.environ["UE_FF_DISABLE_DEFAULT_COMMIT_PREFIX"]

        os.environ["UE_FF_DISABLE_DEFAULT_COMMIT_PREFIX"] = "wrong input"
        with self.assertRaises(ValueError):
            ExtensionInputSerializer(**INPUT)
        del os.environ["UE_FF_DISABLE_DEFAULT_COMMIT_PREFIX"]

        serializer = ExtensionInputSerializer(**INPUT)
        self.assertFalse(serializer.ff_commit_msg)
