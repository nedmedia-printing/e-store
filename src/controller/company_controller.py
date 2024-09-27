from datetime import datetime

from flask import Flask
from sqlalchemy.orm import joinedload

from src.controller import Controllers, error_handler
from src.database.models.bank_accounts import BankAccount
from src.database.models.companies import Company, CompanyBranches, EmployeeRoles, EmployeeDetails, CoverPlanDetails
from src.database.models.contacts import Address, PostalAddress, Contacts
from src.database.models.covers import PolicyRegistrationData, ClientPersonalInformation, PaymentMethods, InsuredParty
from src.database.sql.bank_account import BankAccountORM
from src.database.sql.companies import CompanyORM, CompanyBranchesORM, EmployeeORM, CoverPlanDetailsORM
from src.database.sql.contacts import AddressORM, PostalAddressORM, ContactsORM
from src.database.sql.covers import PolicyRegistrationDataORM, ClientPersonalInformationORM
from src.main import system_cache
from src.utils import create_employee_id

cached_ttl = system_cache.cached_ttl


class CompanyController(Controllers):

    def __init__(self):
        super().__init__()

        self.countries = [
            "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cabo Verde",
            "Cameroon", "Central African Republic", "Chad", "Comoros",
            "Democratic Republic of the Congo", "Republic of the Congo", "Djibouti",
            "Equatorial Guinea", "Eritrea", "Ethiopia", "Gabon", "Gambia", "Ghana",
            "Guinea", "Guinea-Bissau", "Ivory Coast", "Kenya", "Lesotho", "Liberia",
            "Madagascar", "Malawi", "Mali", "Mauritania", "Mauritius", "Mozambique",
            "Namibia", "Niger", "Nigeria", "Rwanda", "Sao Tome and Principe",
            "Senegal", "Seychelles", "Sierra Leone", "Somalia", "South Africa",
            "South Sudan", "Sudan", "Swaziland", "Tanzania", "Togo", "Uganda",
            "Zambia", "Zimbabwe"
        ]

    def init_app(self, app: Flask):
        super().init_app(app=app)

    @error_handler
    async def register_company(self, company: Company) -> Company | None:
        """

        :param company:
        :return:
        """
        with self.get_session() as session:
            company_name = company.company_name.strip().lower()
            company_list = session.query(CompanyORM).filter_by(company_name=company_name).all()
            if company_list:
                self.logger.warning(f"Company with a similar name exists: {company}")
                return None

            company_orm = CompanyORM(**company.dict())
            session.add(company_orm)

            self.logger.info(f"company Created : {company}")
            return company

    @cached_ttl()
    @error_handler
    async def get_company_details(self, company_id: str) -> Company | None:
        with self.get_session() as session:
            company_orm = session.query(CompanyORM).filter_by(company_id=company_id).first()
            if isinstance(company_orm, CompanyORM):
                company_detail = Company(**company_orm.to_dict())
                self.logger.info(f"Found Company Details : {company_detail}")

                return company_detail
            self.logger.info(f"Company Not found: {company_id}")

            return None

    async def get_company_administrator(self, company_id: str) -> EmployeeDetails | None:
        """

        :param company_id:
        :return:
        """
        with self.get_session() as session:
            company_detail_orm = session.query(CompanyORM).filter_by(company_id=company_id).first()
            if isinstance(company_detail_orm, CompanyORM):
                self.logger.info(f"Company Detail ORM : {company_detail_orm.to_dict()}")
                company_detail = Company(**company_detail_orm.to_dict())
                if company_detail.admin_uid:
                    employee_detail_orm = session.query(EmployeeORM).filter_by(uid=company_detail.admin_uid).first()
                    if isinstance(employee_detail_orm, EmployeeORM):
                        self.logger.info(f"Employee Detail ORM : {employee_detail_orm.to_dict(include_relationships=False)}")
                        return EmployeeDetails(**employee_detail_orm.to_dict(include_relationships=False))

            return None

    @error_handler
    async def update_company_details(self, company_details: Company) -> Company | None:
        """

        :param company_details:
        :return:
        """
        with self.get_session() as session:
            company_orm = session.query(CompanyORM).filter_by(company_id=company_details.company_id).first()
            if not isinstance(company_orm, CompanyORM):
                self.logger.warning("Company Not Found cannot Update")
                return None
            if company_details.company_name:
                company_orm.company_name = company_details.company_name
            if company_details.admin_uid:
                company_orm.admin_uid = company_details.admin_uid
            if company_details.reg_ck:
                company_orm.reg_ck = company_details.reg_ck
            if company_details.vat_number:
                company_orm.vat_number = company_details.vat_number

            if company_details.company_description:
                company_orm.company_description = company_details.company_description

            if company_details.company_slogan:
                company_orm.company_slogan = company_details.company_slogan

            if company_details.total_users:
                company_orm.total_users = company_details.total_users

            if company_details.total_clients:
                company_orm.total_clients = company_details.total_clients
            await system_cache.clear_mem_cache()
            return company_details

    @error_handler
    async def delete_company_details(self, company_id: str) -> bool:
        """

        :param company_id:
        :return:
        """
        with self.get_session() as session:
            company_details = session.query(CompanyORM).filter_by(company_id=company_id).first()
            if isinstance(company_details, CompanyORM):
                # TODO Actucally delete company here
                session.delete(company_details)

                return True
            return False

    @error_handler
    async def add_company_branch(self, company_branch: CompanyBranches) -> CompanyBranches | None:
        """

        :param company_branch:
        :return:
        """

        with self.get_session() as session:
            company_branch_orm = CompanyBranchesORM(**company_branch.dict())
            self.logger.info(f"company branch added : {company_branch}")
            session.add(company_branch_orm)
            await system_cache.clear_mem_cache()
            return company_branch

    # noinspection DuplicatedCode
    @error_handler
    async def update_company_branch(self, company_branch: CompanyBranches) -> CompanyBranches | None:
        """

        :param company_branch:
        :return:
        """
        with self.get_session() as session:
            branch_orm = session.query(CompanyBranchesORM).filter_by(branch_id=company_branch.branch_id).first()
            await system_cache.clear_mem_cache()
            if branch_orm:
                # Update the attributes of the retrieved branch record
                if company_branch.branch_name:
                    branch_orm.branch_name = company_branch.branch_name.lower()
                if company_branch.company_id:
                    branch_orm.company_id = company_branch.company_id
                if company_branch.branch_description:
                    branch_orm.branch_description = company_branch.branch_description
                if company_branch.date_registered:
                    branch_orm.date_registered = company_branch.date_registered
                if company_branch.total_clients:
                    branch_orm.total_clients = company_branch.total_clients
                if company_branch.total_employees:
                    branch_orm.total_employees = company_branch.total_employees
                if company_branch.address_id:
                    branch_orm.address_id = company_branch.address_id
                if company_branch.contact_id:
                    branch_orm.contact_id = company_branch.contact_id
                if company_branch.postal_id:
                    branch_orm.postal_id = company_branch.postal_id
                if company_branch.bank_account_id:
                    branch_orm.bank_account_id = company_branch.bank_account_id

                return company_branch

            return None

    @cached_ttl()
    @error_handler
    async def get_company_branches(self, company_id: str) -> list[CompanyBranches]:
        """

        :param company_id:
        :return:
        """
        with self.get_session() as session:
            company_branches_orm = session.query(CompanyBranchesORM).filter_by(company_id=company_id).all()
            return [CompanyBranches(**branch_orm.to_dict()) for branch_orm in company_branches_orm
                    if isinstance(branch_orm, CompanyBranchesORM)]

    @cached_ttl()
    @error_handler
    async def get_branch_by_id(self, branch_id: str) -> CompanyBranches | None:
        """

        :param branch_id:
        :return:
        """
        with self.get_session() as session:
            branch_orm = session.query(CompanyBranchesORM).filter_by(branch_id=branch_id).first()

            if not isinstance(branch_orm, CompanyBranchesORM):
                return None
            return CompanyBranches(**branch_orm.to_dict())

    @cached_ttl()
    @error_handler
    async def get_employee_roles(self, company_id: str) -> list[str]:
        """

        :param company_id:
        :return:
        """
        return EmployeeRoles.get_all_roles()

    # noinspection DuplicatedCode

    @error_handler
    async def add_update_address(self, address: Address) -> Address | None:
        """

        :param address:
        :return:
        """
        with self.get_session() as session:
            branch_address_orm = session.query(AddressORM).filter_by(address_id=address.address_id).first()
            await system_cache.clear_mem_cache()
            if isinstance(branch_address_orm, AddressORM):
                if address.street:
                    branch_address_orm.street = address.street
                if address.city:
                    branch_address_orm.city = address.city
                if address.state_province:
                    branch_address_orm.state_province = address.state_province
                if address.postal_code:
                    branch_address_orm.postal_code = address.postal_code

                return address

            session.add(AddressORM(**address.dict()))
            return address

    @cached_ttl()
    @error_handler
    async def get_address(self, address_id: str) -> Address | None:
        with self.get_session() as session:
            branch_address = session.query(AddressORM).filter_by(address_id=address_id).first()
            if isinstance(branch_address, AddressORM):
                return Address(**branch_address.to_dict())
            return None

    # noinspection DuplicatedCode

    @error_handler
    async def add_postal_address(self, postal_address: PostalAddress) -> PostalAddress | None:
        """
            :param postal_address:
            :return:
        """
        with self.get_session() as session:

            _postal_id = postal_address.postal_id
            branch_postal_orm = session.query(PostalAddressORM).filter_by(postal_id=_postal_id).first()
            await system_cache.clear_mem_cache()
            if isinstance(branch_postal_orm, PostalAddressORM):
                if postal_address.address_line_1:
                    branch_postal_orm.address_line_1 = postal_address.address_line_1
                if postal_address.town_city:
                    branch_postal_orm.town_city = postal_address.town_city
                if postal_address.province:
                    branch_postal_orm.province = postal_address.province
                if postal_address.country:
                    branch_postal_orm.country = postal_address.country
                if postal_address.postal_code:
                    branch_postal_orm.postal_code = postal_address.postal_code

                return postal_address

            session.add(PostalAddressORM(**postal_address.dict()))

            return postal_address

    @cached_ttl()
    @error_handler
    async def get_postal_address(self, postal_id: str) -> PostalAddress | None:
        """

        :param postal_id:
        :return:
        """
        with self.get_session() as session:
            postal_address_orm = session.query(PostalAddressORM).filter_by(postal_id=postal_id).first()
            if isinstance(postal_address_orm, PostalAddressORM):
                return PostalAddress(**postal_address_orm.to_dict())
            return None

    # noinspection DuplicatedCode

    @error_handler
    async def add_contacts(self, contact: Contacts) -> Contacts | None:
        """
        Add branch contacts to the database.

        :param contact: Instance of Contacts containing contact details.
        :return: Added Contacts instance if successful, None otherwise.
        """
        with self.get_session() as session:
            contact_orm = session.query(ContactsORM).filter_by(contact_id=contact.contact_id).first()
            await system_cache.clear_mem_cache()
            if isinstance(contact_orm, ContactsORM):
                # Update existing contact details
                if contact.cell:
                    contact_orm.cell = contact.cell
                if contact.tel:
                    contact_orm.tel = contact.tel
                if contact.email:
                    contact_orm.email = contact.email
                if contact.facebook:
                    contact_orm.facebook = contact.facebook
                if contact.twitter:
                    contact_orm.twitter = contact.twitter
                if contact.whatsapp:
                    contact_orm.whatsapp = contact.whatsapp

                return contact
            # Add new contact details
            session.add(ContactsORM(**contact.dict()))

            return contact

    @cached_ttl()
    @error_handler
    async def get_contact(self, contact_id: str) -> Contacts | None:
        """
        Retrieve branch contact details from the database.

        :param contact_id: The ID of the branch whose contact details to retrieve.
        :return: Contacts instance if found, None otherwise.
        """
        with self.get_session() as session:
            # Query the database for the contact details associated with the given branch_id
            branch_contact_orm = session.query(ContactsORM).filter_by(contact_id=contact_id).first()

            if isinstance(branch_contact_orm, ContactsORM):
                # If contact details exist, create a Contacts instance from the retrieved data
                return Contacts(**branch_contact_orm.to_dict())
            return None

    # noinspection DuplicatedCode

    @error_handler
    async def add_bank_account(self, bank_account: BankAccount) -> BankAccount | None:
        """
        Add or update a branch bank account in the database.

        :param bank_account: Instance of BankAccount containing bank account details.
        :return: Added or updated BankAccount instance if successful, None otherwise.
        """
        with self.get_session() as session:
            bank_account_orm = session.query(BankAccountORM).filter_by(
                bank_account_id=bank_account.bank_account_id).first()
            await system_cache.clear_mem_cache()
            if isinstance(bank_account_orm, BankAccountORM):
                # If the bank account already exists, update its details
                if bank_account.account_holder:
                    bank_account_orm.account_holder = bank_account.account_holder
                if bank_account.account_number:
                    bank_account_orm.account_number = bank_account.account_number
                if bank_account.bank_name:
                    bank_account_orm.bank_name = bank_account.bank_name
                if bank_account.branch:
                    bank_account_orm.branch = bank_account.branch
                if bank_account.account_type:
                    bank_account_orm.account_type = bank_account.account_type

                return bank_account

            # If the bank account does not exist, add it to the database
            session.add(BankAccountORM(**bank_account.dict()))

            return bank_account

    @cached_ttl()
    @error_handler
    async def get_bank_account(self, bank_account_id: str) -> BankAccount | None:
        """

        :param bank_account_id:
        :return:
        """
        with self.get_session() as session:
            bank_account_orm = session.query(BankAccountORM).filter_by(bank_account_id=bank_account_id).first()

            if isinstance(bank_account_orm, BankAccountORM):
                return BankAccount(**bank_account_orm.to_dict())
            return None

    # noinspection DuplicatedCode

    @error_handler
    async def add_update_employee(self, employee: EmployeeDetails) -> tuple[bool, EmployeeDetails | None]:
        """
        **add_employee**
            add or update new employee details
        :param employee:
        :return:
        """
        with self.get_session() as session:

            _id_number = employee.id_number
            employee_orm = session.query(EmployeeORM).filter_by(id_number=_id_number).first()

            await system_cache.clear_mem_cache()

            if isinstance(employee_orm, EmployeeORM):

                if employee.uid:
                    employee_orm.uid = employee.uid
                if employee.company_id:
                    employee_orm.company_id = employee.company_id
                if employee.branch_id:
                    employee_orm.branch_id = employee.branch_id

                if employee.full_names:
                    employee_orm.full_names = employee.full_names
                if employee.last_name:
                    employee_orm.last_name = employee.last_name
                if employee.role:
                    employee_orm.role = employee.role
                if employee.id_number:
                    employee_orm.id_number = employee.id_number
                if employee.email:
                    employee_orm.email = employee.email
                if employee.contact_number:
                    employee_orm.contact_number = employee.contact_number
                if employee.position:
                    employee_orm.position = employee.position
                if employee.date_of_birth:
                    employee_orm.date_of_birth = datetime.strptime(employee.date_of_birth, '%Y-%m-%d').date()
                if employee.date_joined:
                    employee_orm.date_joined = datetime.strptime(employee.date_joined, '%Y-%m-%d').date()
                if employee.salary:
                    employee_orm.salary = employee.salary
                if employee.is_active:
                    employee_orm.is_active = employee.is_active
                if employee.address_id:
                    employee_orm.address_id = employee.address_id
                if employee.postal_id:
                    employee_orm.postal_id = employee.postal_id
                if employee.bank_account_id:
                    employee_orm.bank_account_id = employee.bank_account_id
                if employee.contact_id:
                    employee_orm.contact_id = employee.contact_id

                return True, employee
            try:
                if not employee.employee_id:
                    employee.employee_id = create_employee_id()
                session.add(EmployeeORM(**employee.dict(exclude={'attendance_register'})))
            except Exception as e:
                self.logger.warning(str(e))
            return True, employee

    @cached_ttl()
    @error_handler
    async def get_branch_employees(self, branch_id: str) -> list[EmployeeDetails]:
        """

        :param branch_id:
        :return:
        """
        with self.get_session() as session:
            if not branch_id:
                return []
            employees_orm_list = session.query(EmployeeORM).filter_by(branch_id=branch_id).all()
            return [EmployeeDetails(**employee.to_dict(include_relationships=False)) for employee in
                    employees_orm_list or [] if
                    isinstance(employee, EmployeeORM)]

    @cached_ttl()
    @error_handler
    async def get_branch_policy_holders(self, branch_id: str) -> list[ClientPersonalInformation]:
        with self.get_session() as session:
            policy_holder = InsuredParty.POLICY_HOLDER.value
            clients_orm_list = session.query(ClientPersonalInformationORM).filter_by(branch_id=branch_id,
                                                                                     insured_party=policy_holder).all()
            return [ClientPersonalInformation(**client.to_dict()) for client in clients_orm_list or []]

    @cached_ttl()
    @error_handler
    async def get_branch_policy_holders_with_lapsed_policies(self, branch_id: str) -> list[ClientPersonalInformation]:
        """
        Get policy holders with lapsed policies for a given branch.

        :param branch_id: ID of the branch
        :return: List of ClientPersonalInformation objects
        """
        with self.get_session() as session:
            # Get lapsed policies
            lapsed_policies = session.query(PolicyRegistrationDataORM).filter_by(branch_id=branch_id,
                                                                                 policy_active=False).all()

            # Extract policy numbers of lapsed policies
            policy_numbers = [policy.policy_number for policy in
                              session.query(PolicyRegistrationDataORM).filter_by(
                                  branch_id=branch_id, policy_active=False).all()]

            policy_holders = session.query(ClientPersonalInformationORM) \
                .filter(ClientPersonalInformationORM.policy_number.in_(policy_numbers)) \
                .options(joinedload(ClientPersonalInformationORM.policy_number)) \
                .all()

            # Convert ClientPersonalInformationORM objects to ClientPersonalInformation objects
            return [ClientPersonalInformation(**policy_holder.to_dict()) for policy_holder in policy_holders]

    @cached_ttl()
    @error_handler
    async def get_employee(self, employee_id: str) -> EmployeeDetails | None:
        """

        :param employee_id:
        :return:
        """
        with self.get_session() as session:
            employee_orm = session.query(EmployeeORM).filter_by(employee_id=employee_id).first()
            if isinstance(employee_orm, EmployeeORM):
                return EmployeeDetails(**employee_orm.to_dict(include_relationships=False))
            return None

    @cached_ttl()
    @error_handler
    async def get_employee_by_uid(self, uid: str) -> EmployeeDetails | None:
        """

        :param uid:
        :return:
        """
        with self.get_session() as session:
            employee_orm = session.query(EmployeeORM).filter_by(uid=uid).first()
            if isinstance(employee_orm, EmployeeORM):
                return EmployeeDetails(**employee_orm.to_dict(include_relationships=False))
            return None

    @cached_ttl()
    @error_handler
    async def get_company_employees(self, company_id: str) -> list[EmployeeDetails]:
        """

        :param company_id:
        :return:
        """
        with self.get_session() as session:
            employees_orm_list = session.query(EmployeeORM).filter_by(company_id=company_id).all()
            return [EmployeeDetails(**employee_orm.to_dict()) for employee_orm in employees_orm_list
                    if isinstance(employee_orm, EmployeeORM)]

    # noinspection DuplicatedCode
    @error_handler
    async def create_plan_cover(self, plan_cover: CoverPlanDetails) -> CoverPlanDetails:
        """
        Create or update a cover plan in the database.

        :param plan_cover: CoverPlanDetails instance
        :return: CoverPlanDetails instance
        """
        with self.get_session() as session:
            _plan_name = plan_cover.plan_name.casefold()
            company_id = plan_cover.company_id
            cover_plan_orm = session.query(CoverPlanDetailsORM).filter_by(plan_name=_plan_name,
                                                                          company_id=company_id).first()

            await system_cache.clear_mem_cache()
            if cover_plan_orm:  # If cover plan exists, update its fields
                if plan_cover.company_id:
                    cover_plan_orm.company_id = plan_cover.company_id
                if plan_cover.plan_name:
                    cover_plan_orm.plan_name = plan_cover.plan_name
                if plan_cover.plan_number:
                    cover_plan_orm.plan_number = plan_cover.plan_number
                if plan_cover.plan_type:
                    cover_plan_orm.plan_type = plan_cover.plan_type
                if plan_cover.benefits:
                    cover_plan_orm.benefits = plan_cover.benefits
                if plan_cover.coverage_amount:
                    cover_plan_orm.coverage_amount = plan_cover.coverage_amount
                if plan_cover.premium_costs:
                    cover_plan_orm.premium_costs = plan_cover.premium_costs
                if plan_cover.additional_details:
                    cover_plan_orm.additional_details = plan_cover.additional_details
                if plan_cover.terms_and_conditions:
                    cover_plan_orm.terms_and_conditions = plan_cover.terms_and_conditions
                if plan_cover.inclusions:
                    cover_plan_orm.inclusions = plan_cover.inclusions
                if plan_cover.exclusions:
                    cover_plan_orm.exclusions = plan_cover.exclusions
                if plan_cover.contact_information:
                    cover_plan_orm.contact_information = plan_cover.contact_information
            else:  # If cover plan doesn't exist, create a new entry
                cover_plan_orm = CoverPlanDetailsORM(**plan_cover.dict())
                session.add(cover_plan_orm)

            return plan_cover

    @cached_ttl()
    @error_handler
    async def get_company_covers(self, company_id: str) -> list[CoverPlanDetails]:
        """

        :param company_id:
        :return:
        """
        with self.get_session() as session:
            cover_details_list = session.query(CoverPlanDetailsORM).filter_by(company_id=company_id).all()
            return [CoverPlanDetails(**plan.to_dict()) for plan in cover_details_list
                    if isinstance(plan, CoverPlanDetailsORM)]

    @cached_ttl()
    @error_handler
    async def get_plan_cover(self, company_id: str, plan_number: str) -> CoverPlanDetails | None:
        """

        :param company_id:
        :param plan_number:
        :return:
        """
        with self.get_session() as session:
            plan_cover_orm = session.query(CoverPlanDetailsORM).filter_by(company_id=company_id,
                                                                          plan_number=plan_number).first()
            if isinstance(plan_cover_orm, CoverPlanDetailsORM):
                return CoverPlanDetails(**plan_cover_orm.to_dict())
            return None

    @cached_ttl()
    @error_handler
    async def get_plan_subscribers(self, plan_number: str) -> list[PolicyRegistrationData]:
        """

        :param plan_number:
        :return:
        """
        with self.get_session() as session:
            plan_subscribers = session.query(PolicyRegistrationDataORM).filter_by(plan_number=plan_number).all()
            return [PolicyRegistrationData(**subscriber.to_dict()) for subscriber in plan_subscribers
                    if isinstance(subscriber, PolicyRegistrationDataORM)]

    async def get_plan_subscribers_paged(self, company_id: str, plan_number: str, page: int = 0, count: int = 25):
        """

        :param company_id:
        :param plan_number:
        :param page:
        :param count:
        :return:
        """
        with self.get_session() as session:
            plan_policies_query = (session.query(CoverPlanDetailsORM)
                                   .filter_by(plan_number=plan_number)
                                   .offset(page * count).limit(count + 1))
            plan_policies_orm_list = plan_policies_query.all()
            return [CoverPlanDetails(**policy.to_dict()) for policy in plan_policies_orm_list or []
                    if isinstance(policy, CoverPlanDetailsORM)]

    @cached_ttl(ttl=60)
    @error_handler
    async def get_policy_holders(self, company_id: str) -> list[ClientPersonalInformation]:
        """
            Policy Holders or Clients are the same thing
            Policy Holders are just clients who actually owns the policy
        :param company_id:
        :return:
        """
        with self.get_session() as session:
            # This means we will only obtain policyholders for a specific company
            policy_holder = InsuredParty.POLICY_HOLDER.value
            policy_holders_list = session.query(ClientPersonalInformationORM).filter_by(
                company_id=company_id, insured_party=policy_holder).all()

            return [ClientPersonalInformation(**holder.to_dict()) for holder in policy_holders_list]

    @cached_ttl(ttl=60)
    @error_handler
    async def get_policy_holders_paged(self,
                                       company_id: str,
                                       page: int = 0,
                                       count: int = 25) -> list[ClientPersonalInformation]:
        """
        Fetch paged policyholders for a specific company.

        :param company_id: ID of the company
        :param page: Page number (0-indexed)
        :param count: Number of items per page
        :return: Dictionary with paged results and pagination info
        """
        with self.get_session() as session:
            policy_holder = InsuredParty.POLICY_HOLDER.value
            # Query for paginated results
            policy_holders_query = (
                session.query(ClientPersonalInformationORM)
                .filter_by(company_id=company_id, insured_party=policy_holder)
                .offset(page * count)
                .limit(count + 1)  # Fetch one extra to check if there's a next page
            )
            policy_holders_list = policy_holders_query.all()
            self.logger.info(f"Policy Holders Inside Method: {policy_holders_list}")

            # Convert ORM results to data models
            return [ClientPersonalInformation(**holder.to_dict()) for holder in policy_holders_list]

    @cached_ttl()
    @error_handler
    async def get_policy_holder(self, uid: str) -> ClientPersonalInformation | None:
        with self.get_session() as session:
            policy_holder_orm = session.query(ClientPersonalInformationORM).filter_by(uid=uid).first()
            if isinstance(policy_holder_orm, ClientPersonalInformationORM):
                return ClientPersonalInformation(**policy_holder_orm.to_dict())
            return None

    @cached_ttl()
    @error_handler
    async def get_policy_data(self, policy_number: str) -> PolicyRegistrationData | None:
        with self.get_session() as session:
            policy_data_orm = (
                session.query(PolicyRegistrationDataORM)
                .filter_by(policy_number=policy_number)
                .options(joinedload(PolicyRegistrationDataORM.premiums))  # Load related premiums
                .first()
            )
            if isinstance(policy_data_orm, PolicyRegistrationDataORM):
                return PolicyRegistrationData(**policy_data_orm.to_dict())
            return None

    @cached_ttl()
    @error_handler
    async def get_beneficiaries(self, policy_number: str):
        """

        :param policy_number:
        :return:
        """
        with self.get_session() as session:
            beneficiaries_list_orm = session.query(ClientPersonalInformationORM).filter_by(
                policy_number=policy_number).all()
            return [ClientPersonalInformation(**client.to_dict()) for client in beneficiaries_list_orm]

    @error_handler
    async def get_payment_methods(self) -> list[str]:
        return PaymentMethods.get_payment_methods()

    # noinspection DuplicatedCode
    @error_handler
    async def add_policy_holder(self, policy_holder: ClientPersonalInformation) -> ClientPersonalInformation:
        """
        Add or update a policy holder in the database.
        :param policy_holder: ClientPersonalInformation instance
        :return: None
        """
        with self.get_session() as session:
            uid = policy_holder.uid

            # Check if the policy holder exists in the database
            policy_holder_orm = session.query(ClientPersonalInformationORM).filter_by(
                uid=uid).first()

            await system_cache.clear_mem_cache()
            if policy_holder_orm:
                # Update the existing policy holder
                if policy_holder.branch_id:
                    policy_holder_orm.branch_id = policy_holder.branch_id
                if policy_holder.company_id:
                    policy_holder_orm.company_id = policy_holder.company_id
                if policy_holder.title:
                    policy_holder_orm.title = policy_holder.title
                if policy_holder.full_names:
                    policy_holder_orm.full_names = policy_holder.full_names
                if policy_holder.surname:
                    policy_holder_orm.surname = policy_holder.surname
                if policy_holder.id_number:
                    policy_holder_orm.id_number = policy_holder.id_number
                if policy_holder.date_of_birth:
                    policy_holder_orm.date_of_birth = policy_holder.date_of_birth
                if policy_holder.nationality:
                    policy_holder_orm.nationality = policy_holder.nationality
                if policy_holder.policy_number:
                    policy_holder_orm.policy_number = policy_holder.policy_number
                if policy_holder.insured_party:
                    policy_holder_orm.insured_party = policy_holder.insured_party
                if policy_holder.address_id:
                    policy_holder_orm.address_id = policy_holder.address_id
                if policy_holder.contact_id:
                    policy_holder_orm.contact_id = policy_holder.contact_id
                if policy_holder.postal_id:
                    policy_holder_orm.postal_id = policy_holder.postal_id
                if policy_holder.bank_account_id:
                    policy_holder_orm.bank_account_id = policy_holder.bank_account_id
            else:
                # Create a new policy holder
                policy_holder_orm = ClientPersonalInformationORM(**policy_holder.dict())
                session.add(policy_holder_orm)

            # Commit changes to the database

            return policy_holder

    # noinspection DuplicatedCode
    @error_handler
    async def add_policy_data(self, policy_data: PolicyRegistrationData) -> PolicyRegistrationData:
        """
        Add or update policy data in the database.

        :param policy_data: PolicyRegistrationData instance
        :return: PolicyRegistrationData instance
        """
        with self.get_session() as session:
            uid = policy_data.uid
            branch_id = policy_data.branch_id
            company_id = policy_data.company_id

            # Query the database to check if the policy data already exists
            policy_data_orm = session.query(PolicyRegistrationDataORM).filter_by(
                uid=uid, company_id=company_id).first()
            await system_cache.clear_mem_cache()
            if policy_data_orm:
                # Update all fields for the existing policy data
                if branch_id:
                    policy_data_orm.branch_id = branch_id
                if company_id:
                    policy_data_orm.company_id = company_id

                if policy_data.policy_number:
                    policy_data_orm.policy_number = policy_data.policy_number
                if policy_data.plan_number:
                    policy_data_orm.plan_number = policy_data.plan_number

                if policy_data.policy_type:
                    policy_data_orm.policy_type = policy_data.policy_type
                if policy_data.total_family_members:
                    policy_data_orm.total_family_members = policy_data.total_family_members
                if policy_data.total_premiums:
                    policy_data_orm.total_premiums = policy_data.total_premiums
                if policy_data.payment_code_reference:
                    policy_data_orm.payment_code_reference = policy_data.payment_code_reference
                if policy_data.date_activated:
                    policy_data_orm.date_activated = policy_data.date_activated
                if policy_data.first_premium_date:
                    policy_data_orm.first_premium_date = policy_data.first_premium_date
                if policy_data.payment_day:
                    policy_data_orm.payment_day = policy_data.payment_day
                if policy_data.client_signature:
                    policy_data_orm.client_signature = policy_data.client_signature
                if policy_data.employee_signature:
                    policy_data_orm.employee_signature = policy_data.employee_signature
                if policy_data.payment_method:
                    policy_data_orm.payment_method = policy_data.payment_method
                if policy_data.policy_active in [True, False]:
                    policy_data_orm.policy_active = policy_data.policy_active
            else:
                # Create a new policy data entry
                policy_data_orm = PolicyRegistrationDataORM(**policy_data.dict(exclude={'premiums'}))
                session.add(policy_data_orm)

            return policy_data

    @cached_ttl()
    @error_handler
    async def get_countries(self) -> list[str]:
        return self.countries

    @cached_ttl()
    @error_handler
    async def get_policy_with_policy_number(self, policy_number: str) -> PolicyRegistrationData | None:
        """

        :param policy_number:
        :return:
        """
        with self.get_session() as session:
            policy_data_orm = session.query(PolicyRegistrationDataORM).filter_by(policy_number=policy_number).first()
            if isinstance(policy_data_orm, PolicyRegistrationDataORM):
                return PolicyRegistrationData(**policy_data_orm.to_dict())
            return None

    @cached_ttl()
    @error_handler
    async def search_policies_by_id_number(self, id_number: str) -> list[PolicyRegistrationData]:
        """
        Search for policies by ID number.
        :param id_number: The ID number of the client to search for.
        :return: List of policies associated with the ID number.
        """
        with self.get_session() as session:
            # Perform a single query to fetch policies by ID number
            policies_orm = session.query(PolicyRegistrationDataORM) \
                .join(ClientPersonalInformationORM,
                      ClientPersonalInformationORM.policy_number == PolicyRegistrationDataORM.policy_number) \
                .filter(ClientPersonalInformationORM.id_number == id_number) \
                .all()

            # Convert ORM objects to PolicyRegistrationData objects
            return [PolicyRegistrationData(**policy_orm.to_dict()) for policy_orm in policies_orm]

    @cached_ttl()
    @error_handler
    async def search_policies_by_policy_number(self, policy_number: str) -> list[PolicyRegistrationData]:
        """

        :param policy_number:
        :return:
        """
        with self.get_session() as session:
            policy_data_orm_list = session.query(PolicyRegistrationDataORM).filter_by(policy_number=policy_number).all()
            return [PolicyRegistrationData(**policy_orm.to_dict()) for policy_orm in policy_data_orm_list
                    if isinstance(policy_orm, PolicyRegistrationDataORM)]

    @cached_ttl()
    @error_handler
    async def search_policies_by_policy_holder_name(self, policy_holder_name: str) -> list[PolicyRegistrationData]:
        """
            Search for policies by policyholders name.
            :param policy_holder_name: The name of the policyholders to search for.
            :return: List of policies matching the policyholders name.
        """
        with self.get_session() as session:
            # Perform a single query to fetch policies by policyholders name
            policies_orm = (
                session.query(PolicyRegistrationDataORM)
                .join(ClientPersonalInformationORM,
                      ClientPersonalInformationORM.policy_number == PolicyRegistrationDataORM.policy_number)
                .filter(ClientPersonalInformationORM.full_names == policy_holder_name)
                .all())

            # Convert ORM objects to PolicyRegistrationData objects
            return [PolicyRegistrationData(**policy_orm.to_dict()) for policy_orm in policies_orm]

    @cached_ttl()
    @error_handler
    async def return_all_active_company_policies(self) -> list[PolicyRegistrationData]:
        """

        :return:
        """
        with self.get_session() as session:
            policies_orm_list = session.query(PolicyRegistrationDataORM).filter_by(policy_active=True).all()
            return [PolicyRegistrationData(**policy.to_dict()) for policy in policies_orm_list]

    @cached_ttl()
    @error_handler
    async def return_all_active_company_policies_paged(self, company_id: str, page: int = 0,
                                                       count: int = 25) -> list[PolicyRegistrationData]:
        """
        Fetch paged results of active company policies.

        :param company_id:
        :param page: Page number starting from 0.
        :param count: Number of records per page.
        :return: List of PolicyRegistrationData.
        """
        with self.get_session() as session:
            policies_orm_list = (
                session.query(PolicyRegistrationDataORM)
                .filter_by(policy_active=True, company_id=company_id)
                .offset(page * count)
                .limit(count)
                .all()
            )
            return [PolicyRegistrationData(**policy.to_dict()) for policy in policies_orm_list]

    @cached_ttl()
    @error_handler
    async def return_all_lapsed_company_policies_paged(self, company_id: str, page: int = 0,
                                                       count: int = 25) -> list[PolicyRegistrationData]:
        """
        Fetch paged results of active company policies.

        :param company_id:
        :param page: Page number starting from 0.
        :param count: Number of records per page.
        :return: List of PolicyRegistrationData.
        """
        with self.get_session() as session:
            policies_orm_list = (
                session.query(PolicyRegistrationDataORM)
                .filter_by(policy_active=False, company_id=company_id)
                .offset(page * count)
                .limit(count)
                .all()
            )
            return [PolicyRegistrationData(**policy.to_dict()) for policy in policies_orm_list]

    @cached_ttl()
    @error_handler
    async def return_all_outstanding_company_policies(self) -> list[PolicyRegistrationData]:
        """

        :return:
        """
        with self.get_session() as session:
            policies_orm_list = session.query(PolicyRegistrationDataORM).filter_by(policy_active=False).all()
            return [PolicyRegistrationData(**policy.to_dict()) for policy in policies_orm_list]
