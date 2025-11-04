import os


def test_secrets_from_env():
    os.environ["TEST_API_SECRET"] = "s3cr3t"
    assert os.getenv("TEST_API_SECRET") == "s3cr3t"
