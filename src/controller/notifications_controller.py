import asyncio
from datetime import datetime, timedelta

from flask import Flask

from src.controller import Controllers, error_handler
from src.controller.auth import UserController
from src.controller.messaging_controller import MessagingController


class SubscriptionExpiredException(Exception):
    """Exception raised when a subscription is expired."""

    def __init__(self, message="Subscription is expired."):
        self.message = message
        super().__init__(self.message)


async def create_sleep_duration():
    now = datetime.now()
    # Calculate the time until the next execution time (e.g., 9:00 AM)
    next_execution_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if now >= next_execution_time:
        next_execution_time += timedelta(days=1)  # Move to the next day if already past execution time
    sleep_duration = (next_execution_time - now).total_seconds()
    return sleep_duration


class NotificationsController(Controllers):

    def __init__(self):
        super().__init__()
        self.messaging_controller: MessagingController | None = None

        self.user_controller: UserController | None = None
        self.loop = asyncio.get_event_loop()

    @staticmethod
    async def template_message(company_data, date_str, day_name, holder, policy_registration_data):
        """
            template message for payment reminder
        :param company_data:
        :param date_str:
        :param day_name:
        :param holder:
        :param policy_registration_data:
        :return:
        """
        _message = f"""
                                {company_data.company_name}

                                Premium Payment Reminder
                                Hello {holder.full_names} {holder.surname}

                                This is to remind you that your next premium payment date will be on 

                                {day_name} {date_str}

                                Please be sure to make payment on or before this date.

                                Next Premium Amount : R {policy_registration_data.total_premiums}.00

                                Thank You. 
                                """
        return _message

    # noinspection PyMethodOverriding
    def init_app(self, app: Flask, messaging_controller: MessagingController, company_controller: CompanyController,
                 user_controller: UserController):
        """
        **init_app**

            :param user_controller:
            :param company_controller:
            :param messaging_controller:
            :param app:
            :return:
        """
        super().init_app(app=app)
        self.messaging_controller = messaging_controller
        self.company_controller = company_controller
        self.user_controller = user_controller
        self.loop.create_task(self.daemon_runner())


    @error_handler
    async def execute_reminders(self):
        """
            This Method will go through all the covers and all clients
            then send payment reminders to every client
        :return:
        """
        with self.get_session() as session:
            pass

    async def daemon_runner(self):
        """
        Daemon runner that checks if it's time to execute send_payment_reminders,
        sleeps until the next execution time, and then executes the reminders.

        :return: None
        """
        self.logger.info("Started Notifications Daemon")

        while True:
            # Schedule the payment reminders task to run at the next execution time
            await self.execute_reminders()
            # Sleep until the next execution time
            sleep_duration = await create_sleep_duration()
            await asyncio.sleep(sleep_duration)
