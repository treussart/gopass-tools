import os
from unittest import mock

from export import (
    extract_infos_from_show,
    extract_infos_from_path,
    get_infos,
    get_secrets_path,
    write_csv,
    GOOGLE_FORMAT,
    FILE_NAME,
)

infos_all = """password
comment:
url: https://domain.tld
username: username
"""

infos_some = """password
---
user: username
"""

infos_password = """password
"""

infos_binary = """azeazeazeaze
azeazeazeaze
azeazeazeaze
azeazeazeaze
"""

path_account = "Account/domain.tld"
path_normal = "domain.tld/username"
path_short = "domain.tld"
path_long = "company/division/websites/domain.tld/user@domain.tld"
path_without_url = "company/division/common/CAT"


class TestExtractInfosFromShow:
    def test_all(self):
        assert extract_infos_from_show(infos_all) == (
            "domain.tld",
            "https://domain.tld",
            "username",
            "password",
            False,
        )

    def test_some(self):
        assert extract_infos_from_show(infos_some) == (
            None,
            None,
            "username",
            "password",
            False,
        )

    def test_just_password(self):
        assert extract_infos_from_show(infos_password) == (
            None,
            None,
            None,
            "password",
            False,
        )

    def test_binary(self):
        assert extract_infos_from_show(infos_binary) == (
            None,
            None,
            None,
            "azeazeazeaze\nazeazeazeaze\nazeazeazeaze\nazeazeazeaze\n",
            True,
        )


class TestExtractInfosFromPath:
    def test_account(self):
        assert extract_infos_from_path(path_account) == ("domain.tld", "domain.tld")

    def test_normal(self):
        assert extract_infos_from_path(path_normal) == ("domain.tld", "username")

    def test_short(self):
        assert extract_infos_from_path(path_short) == ("domain.tld", "domain.tld")

    def test_long(self):
        assert extract_infos_from_path(path_long) == ("domain.tld", "user@domain.tld")

    def test_without_url(self):
        assert extract_infos_from_path(path_without_url) == (None, "CAT")


class TestGetInfos:
    def test_path_account(self):
        assert get_infos(path_account, infos_all) == (
            "domain.tld",
            "https://domain.tld",
            "username",
            "password",
            False,
        )
        assert get_infos(path_account, infos_some) == (
            "domain.tld",
            "domain.tld",
            "username",
            "password",
            False,
        )
        assert get_infos(path_account, infos_password) == (
            "domain.tld",
            "domain.tld",
            "domain.tld",
            "password",
            False,
        )

    def test_path_without_url(self):
        assert get_infos(path_without_url, infos_all) == (
            "domain.tld",
            "https://domain.tld",
            "username",
            "password",
            False,
        )
        assert get_infos(path_without_url, infos_some) == (
            "",
            "",
            "username",
            "password",
            False,
        )
        assert get_infos(path_without_url, infos_password) == (
            "",
            "",
            "CAT",
            "password",
            False,
        )


class TestGetSecretsPath:
    @mock.patch("subprocess.getstatusoutput")
    def test_one(self, mock_subproc_getstatusoutput):
        mock_subproc_getstatusoutput.return_value = (0, "test")
        assert get_secrets_path() == ["test"]

    @mock.patch("subprocess.getstatusoutput")
    def test_multiple(self, mock_subproc_getstatusoutput):
        mock_subproc_getstatusoutput.return_value = (0, "test\ntest")
        assert get_secrets_path() == ["test", "test"]


class TestWriteCsv:
    @mock.patch("subprocess.getstatusoutput")
    def test_all(self, mock_subproc_getstatusoutput):
        mock_subproc_getstatusoutput.return_value = (0, infos_all)
        write_csv(
            GOOGLE_FORMAT,
            [path_account, path_normal, path_long, path_short, path_without_url],
        )
        assert os.path.isfile(FILE_NAME)

    @mock.patch("subprocess.getstatusoutput")
    def test_password(self, mock_subproc_getstatusoutput):
        mock_subproc_getstatusoutput.return_value = (0, infos_password)
        write_csv(
            GOOGLE_FORMAT,
            [path_account, path_normal, path_long, path_short, path_without_url],
        )
        assert os.path.isfile(FILE_NAME)
