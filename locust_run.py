from locust import HttpUser, task


class WebsiteUser(HttpUser):
    @task
    def load_test(self):
        self.client.get("https://funeral-manager.org")
