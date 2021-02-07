import urequests
import uhashlib


class Senko:
    github = 'https://raw.githubusercontent.com'

    def __init__(self, files, user, repo, url=None, branch='master', working_dir='app', headers=[]):
        """Senko OTA agent class.

        Args:
            user (str): github user
            repo (str): github repo to fetch
            branch (str): github repo branch to fetch: default master
            working_dir (str): directory inside github repo wheren the micropython app is at
            url (str): URL to root directory.
            files (list): Files included in OTA update.
            headers (list, optional): Headers for urequests.
        """
        self.base_url = '{}/{}/{}'.format(self.github, user, repo)
        self.url = url if url is not None else '{}/{}/{}'.format(self.base_url, branch, working_dir)
        self.headers = headers

        self.files = files

    def _check_hash(self, x, y):
        x_hash = uhashlib.sha1(x.encode())
        y_hash = uhashlib.sha1(y.encode())

        x = x_hash.digest()
        y = y_hash.digest()

        if str(x) == str(y):
            return True
        else:
            return False

    def _get_file(self, url):
        payload = urequests.get(url, headers=self.headers)
        code = payload.status_code

        if code == 200:
            return payload.text
        else:
            return None

    def _check_all(self):
        changes = []

        for file in self.files:
            latest_version = self._get_file(self.url + "/" + file)
            if latest_version is None:
                return []

            try:
                with open(file, "r") as local_file:
                    local_version = local_file.read()
            except:
                local_version = ""

            if not self._check_hash(latest_version, local_version):
                changes.append(file)

        return changes

    def fetch(self):
        """Check if newer version is available.

        Returns:
            True - if is, False - if not.
        """
        if not self._check_all():
            return False
        else:
            return True

    def update(self):
        """Replace all changed files with newer one.

        Returns:
            True - if changes were made, False - if not.
        """
        changes = self._check_all()

        for file in changes:
            with open(file, "w") as local_file:
                local_file.write(self._get_file(self.url + "/" + file))

        if changes:
            return True
        else:
            return False
