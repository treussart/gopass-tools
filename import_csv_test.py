from import_csv import extract_infos, generate_template, get_cmd

template_full = "pass\"w'o#rd\ncomment:\nurl: http://domain.tld\nusername: username"


class TestExtractInfos:
    def test_simple(self):
        assert extract_infos(
            dict(name="name", url="url", password="password", username="username")
        ) == ("websites/name/username", "url", "username", "password")

    def test_not_name(self):
        assert extract_infos(
            dict(name="", url="url", password="password", username="username")
        ) == (None, None, None, None)


class TestGenerateTemplate:
    def test_simple(self):
        assert (
                generate_template("http://domain.tld", "username", "password")
                == "password\ncomment:\nurl: http://domain.tld\nusername: username"
        )

    def test_complex(self):
        assert (
                generate_template("http://domain.tld", "username", "pass\"w'o#rd")
                == template_full
        )


class TestGetCmd:
    def test_simple(self):
        assert (
                get_cmd(template_full, "websites/name/username")
                == """cat tmp.txt | gopass insert -f websites/name/username"""
        )
