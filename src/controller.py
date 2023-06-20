import requests
import json


class Gns3Project:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __str__(self):
        return f"{self.name} ({self.project_id})"


class Gns3Controller:
    def __init__(self, host: str = "127.0.0.1", port: int = 3080):
        self.host = host
        self.port = port

    def __query(self, uri):
        url = f"http://{self.host}:{self.port}{uri}"
        result = requests.get(url)
        if result.status_code == 200:
            return result.json()
        return None

    def __delete(self, uri):
        url = f"http://{self.host}:{self.port}{uri}"
        result = requests.delete(url)
        if result.status_code == 200:
            return True
        return False

    def __put(self, uri: str, data: dict):
        url = f"http://{self.host}:{self.port}{uri}"
        headers = {"Content-Type": "application/json"}
        result = requests.put(url, params=data, headers=headers)
        if result.status_code == 200:
            return True
        return False

    def __post(self, uri: str, data: dict):
        url = f"http://{self.host}:{self.port}{uri}"
        result = requests.post(url, params=data)
        if result.status_code == 200:
            return True
        return False

    def __get_version(self):
        uri = "/v2/version"
        return self.__query(uri=uri)

    def __get_projects(self):
        uri = "/v2/projects"
        return self.__query(uri=uri)

    def get_project(self,project_id):
        uri = f"/v2/projects/{project_id}"
        return self.__query(uri)

    def get_projects(self):
        projects = self.__get_projects()
        return [Gns3Project(**project) for project in projects]

    def delete_project(self, project_id):
        uri = f"/v2/projects/{project_id}"
        self.__delete(uri)

    def update_project(self, project_id, data):
        uri = f"/v2/projects/{project_id}"
        self.__put(uri, data)

    def duplicate_project(self, project_id, new_data):
        uri = f"/v2/projects/{project_id}/duplicate"
        self.__post(uri, new_data)
