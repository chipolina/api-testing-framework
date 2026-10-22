import allure
import requests


class ApiClient:
    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {"Accept": "application/json"}
        )

    def _build_url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def close(self) -> None:
        self.session.close()

    def get(self, path: str) -> requests.Response:
        return self.request("GET", path=path, timeout=self.timeout)

    def post(self, path: str, json: dict) -> requests.Response:
        return self.request("POST", path=path, json=json, timeout=self.timeout)

    def put(self, path: str, json: dict) -> requests.Response:
        return self.request("PUT", path=path, json=json, timeout=self.timeout)

    def delete(self, path: str) -> requests.Response:
        return self.request("DELETE", path=path, timeout=self.timeout)

    def patch(self, path: str, json: dict) -> requests.Response:
        return self.request("PATCH", path=path, json=json, timeout=self.timeout)


    @allure.step("HTTP {method} {path}")
    def request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> requests.Response:
        url = self._build_url(path)
        kwargs.setdefault("timeout", self.timeout)

        with allure.step("Attach HTTP request details"):
            allure.attach(
                f"{method} {url}",
                name="Request URL",
                attachment_type=allure.attachment_type.TEXT,
            )

            if "json" in kwargs:
                import json

                allure.attach(
                    json.dumps(kwargs["json"], indent=2, ensure_ascii=False),
                    name="Request body",
                    attachment_type=allure.attachment_type.JSON,
                )

        response = self.session.request(method, url, **kwargs)

        with allure.step("Attach HTTP response details"):
            allure.attach(
                str(response.status_code),
                name="HTTP status",
                attachment_type=allure.attachment_type.TEXT,
            )
            allure.attach(
                response.text,
                name="Response body",
                attachment_type=allure.attachment_type.TEXT,
            )

        return response

