"""
URL Configuration for Accpick Debtor Management System API.

Provides RESTful endpoints for all resources with automatic router registration.
"""
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    DebtorAreaViewSet,
    SalesDepartmentViewSet,
    DebtorViewSet,
    DebtorTransactionViewSet,
    DebtorOpenViewSet,
    DebtorJournalViewSet,
    PostDatedChequeViewSet,
    InterestChargeViewSet,
    ReceiptAllocationViewSet,
)

# Create router and register viewsets
router = DefaultRouter()

# Register all viewsets
router.register(r'areas', DebtorAreaViewSet, basename='debtorarea')
router.register(r'departments', SalesDepartmentViewSet, basename='salesdepartment')
router.register(r'debtors', DebtorViewSet, basename='debtor')
router.register(r'transactions', DebtorTransactionViewSet, basename='debtortransaction')
router.register(r'open-items', DebtorOpenViewSet, basename='debtoropen')
router.register(r'journals', DebtorJournalViewSet, basename='debtorjournal')
router.register(r'post-dated-cheques', PostDatedChequeViewSet, basename='postdatedcheque')
router.register(r'interest-charges', InterestChargeViewSet, basename='interestcharge')
router.register(r'receipt-allocations', ReceiptAllocationViewSet, basename='receiptallocation')

# HTML URL patterns
html_patterns = [
    path('', RedirectView.as_view(url='dashboard/'), name='index'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('accounts/', views.AccountListView.as_view(), name='account_list'),
    path('accounts/create/', views.AccountCreateView.as_view(), name='account_create'),
    path('accounts/<str:pk>/', views.AccountDetailView.as_view(), name='account_detail'),
    path('accounts/<str:pk>/edit/', views.AccountUpdateView.as_view(), name='account_update'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction_enquiry'),
    path('age-analysis/', views.AgeAnalysisView.as_view(), name='age_analysis'),
    path('debit-journal/', views.DebitJournalView.as_view(), name='debit_journal'),
    path('credit-journal/', views.CreditJournalView.as_view(), name='credit_journal'),
    path('batch-receipt/', views.BatchReceiptView.as_view(), name='batch_receipt'),
    path('pdc/', views.PDCListView.as_view(), name='pdc_list'),
    path('interest-charging/', views.InterestChargingView.as_view(), name='interest_charging'),
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('sales-areas/', views.SalesAreasListView.as_view(), name='sales_areas_list'),
    path('departments/', views.DepartmentsListView.as_view(), name='departments_list'),
    path('account-balances/', views.AccountBalancesView.as_view(), name='account_balances'),
    path('top-accounts/', views.TopAccountsView.as_view(), name='top_accounts'),
    path('individual-account/', views.IndividualAccountView.as_view(), name='account_enquiry'),
]

# URL patterns
urlpatterns = html_patterns + [
    # Include router URLs
    path('api/', include(router.urls)),
]

"""
API ENDPOINTS DOCUMENTATION
============================

DEBTOR AREAS / SALESMEN
-----------------------
GET     /api/areas/                         - List all areas/salesmen
POST    /api/areas/                         - Create new area/salesman
GET     /api/areas/{id}/                    - Retrieve specific area/salesman
PUT     /api/areas/{id}/                    - Update area/salesman
PATCH   /api/areas/{id}/                    - Partial update area/salesman
DELETE  /api/areas/{id}/                    - Delete area/salesman
GET     /api/areas/{id}/sales_performance/  - Get sales performance for area
GET     /api/areas/{id}/debtors/            - Get all debtors in area

SALES DEPARTMENTS
-----------------
GET     /api/departments/                         - List all departments
POST    /api/departments/                         - Create new department
GET     /api/departments/{id}/                    - Retrieve specific department
PUT     /api/departments/{id}/                    - Update department
PATCH   /api/departments/{id}/                    - Partial update department
DELETE  /api/departments/{id}/                    - Delete department
GET     /api/departments/{id}/sales_performance/  - Get sales performance for department

DEBTORS / CUSTOMERS
-------------------
GET     /api/debtors/                       - List all debtors (lightweight)
POST    /api/debtors/                       - Create new debtor
GET     /api/debtors/{id}/                  - Retrieve specific debtor (full details)
PUT     /api/debtors/{id}/                  - Update debtor
PATCH   /api/debtors/{id}/                  - Partial update debtor
DELETE  /api/debtors/{id}/                  - Delete debtor
GET     /api/debtors/over_credit_limit/     - Get debtors over credit limit
GET     /api/debtors/blocked_accounts/      - Get blocked accounts
GET     /api/debtors/with_balances/         - Get debtors with non-zero balances
GET     /api/debtors/{id}/transactions/     - Get all transactions for debtor
GET     /api/debtors/{id}/open_items/       - Get all open items for debtor
GET     /api/debtors/{id}/age_analysis/     - Get aging analysis for debtor
GET     /api/debtors/{id}/statement/        - Generate statement for debtor
POST    /api/debtors/{id}/update_aging/     - Manually trigger aging update

Query Parameters for list:
- blockflag: Filter by blocked status (true/false)
- acctype: Filter by account type (blank/O/C)
- darea: Filter by area/salesman code
- search: Search by account number, name, short name, tel, email

DEBTOR TRANSACTIONS
-------------------
GET     /api/transactions/                  - List all transactions
POST    /api/transactions/                  - Create new transaction
GET     /api/transactions/{id}/             - Retrieve specific transaction
PUT     /api/transactions/{id}/             - Update transaction
PATCH   /api/transactions/{id}/             - Partial update transaction
DELETE  /api/transactions/{id}/             - Delete transaction
GET     /api/transactions/by_type/          - Get transactions by type (requires ?type=)
GET     /api/transactions/current_period/   - Get current month transactions
GET     /api/transactions/gross_profit_report/ - Get gross profit report

Query Parameters for list:
- debtor: Filter by debtor account number
- dtype: Filter by transaction type (INV/CRN/CSH/etc.)
- dtdate: Filter by transaction date
- department: Filter by department number
- search: Search by transaction number, order number, customer reference

DEBTOR OPEN ITEMS
-----------------
GET     /api/open-items/                    - List all open items
POST    /api/open-items/                    - Create new open item
GET     /api/open-items/{id}/               - Retrieve specific open item
PUT     /api/open-items/{id}/               - Update open item
PATCH   /api/open-items/{id}/               - Partial update open item
DELETE  /api/open-items/{id}/               - Delete open item
GET     /api/open-items/outstanding/        - Get outstanding open items
GET     /api/open-items/aged_report/        - Get aged open items report

Query Parameters for list:
- debtor: Filter by debtor account number
- posted: Filter by posted status (true/false)
- ageflag: Filter by aging period (1-7)
- type: Filter by transaction type

DEBTOR JOURNALS
---------------
GET     /api/journals/                      - List all journals
POST    /api/journals/                      - Create new journal
GET     /api/journals/{id}/                 - Retrieve specific journal
PUT     /api/journals/{id}/                 - Update journal
PATCH   /api/journals/{id}/                 - Partial update journal
DELETE  /api/journals/{id}/                 - Delete journal
POST    /api/journals/post_batch/           - Post a batch of journals (requires batch_no)

Query Parameters for list:
- debtor: Filter by debtor account number
- journal_type: Filter by journal type (DBJ/CRJ)
- posted: Filter by posted status (true/false)
- batch_no: Filter by batch number
- search: Search by journal number or reference

POST-DATED CHEQUES
------------------
GET     /api/post-dated-cheques/            - List all PDCs
POST    /api/post-dated-cheques/            - Create new PDC
GET     /api/post-dated-cheques/{id}/       - Retrieve specific PDC
PUT     /api/post-dated-cheques/{id}/       - Update PDC
PATCH   /api/post-dated-cheques/{id}/       - Partial update PDC
DELETE  /api/post-dated-cheques/{id}/       - Delete PDC
GET     /api/post-dated-cheques/due_today/  - Get PDCs due today
GET     /api/post-dated-cheques/due_tomorrow/ - Get PDCs due tomorrow
GET     /api/post-dated-cheques/overdue/    - Get overdue PDCs
POST    /api/post-dated-cheques/{id}/process/ - Mark PDC as processed
POST    /api/post-dated-cheques/{id}/cancel/  - Mark PDC as cancelled

Query Parameters for list:
- debtor: Filter by debtor account number
- processed: Filter by processed status (true/false)
- cancelled: Filter by cancelled status (true/false)
- search: Search by cheque number or bank name

INTEREST CHARGES
----------------
GET     /api/interest-charges/              - List all interest charges
POST    /api/interest-charges/              - Create new interest charge
GET     /api/interest-charges/{id}/         - Retrieve specific interest charge
POST    /api/interest-charges/calculate_interest/ - Calculate interest for eligible debtors

Query Parameters for list:
- debtor: Filter by debtor account number
- posted: Filter by posted status (true/false)
- charge_date: Filter by charge date

Calculate Interest POST body:
{
    "charge_date": "2024-01-31",
    "start_period": "2",
    "interest_rate": "1.5",
    "pay_on_credit": false
}

RECEIPT ALLOCATIONS
-------------------
GET     /api/receipt-allocations/           - List all receipt allocations
POST    /api/receipt-allocations/           - Create new allocation
GET     /api/receipt-allocations/{id}/      - Retrieve specific allocation
PUT     /api/receipt-allocations/{id}/      - Update allocation
PATCH   /api/receipt-allocations/{id}/      - Partial update allocation
DELETE  /api/receipt-allocations/{id}/      - Delete allocation

Query Parameters for list:
- receipt_transaction: Filter by receipt transaction ID
- open_item: Filter by open item ID
- fully_paid: Filter by fully paid status (true/false)

COMMON QUERY PARAMETERS
-----------------------
All list endpoints support:
- ordering: Order results by field (prefix with - for descending)
  Example: ?ordering=-dtdate
- page: Page number for pagination
- page_size: Number of results per page

AUTHENTICATION
--------------
All endpoints require authentication. Include token in header:
Authorization: Bearer {your-token}

ERROR RESPONSES
---------------
400 Bad Request - Invalid data or validation error
401 Unauthorized - Authentication required
403 Forbidden - Permission denied
404 Not Found - Resource not found
500 Internal Server Error - Server error

EXAMPLE REQUESTS
----------------

1. Create a new debtor:
POST /api/debtors/
{
    "dno": "CUST001",
    "dname": "ABC Company",
    "dsname": "ABC",
    "dtel": "0312345678",
    "email": "info@abc.com",
    "darea": "1",
    "dclimit": "50000.00",
    "terms": "30",
    "acctype": ""
}

2. Get debtor with transactions:
GET /api/debtors/CUST001/transactions/?start_date=2024-01-01&end_date=2024-01-31

3. Create a transaction:
POST /api/transactions/
{
    "debtor": "CUST001",
    "dtrano": "INV001",
    "dtdate": "2024-01-15",
    "dtype": "INV",
    "dttot": "1500.00",
    "dtgst": "225.00"
}

4. Get age analysis for all debtors:
GET /api/debtors/?ordering=dposbal

5. Get overdue PDCs:
GET /api/post-dated-cheques/overdue/

6. Calculate interest:
POST /api/interest-charges/calculate_interest/
{
    "charge_date": "2024-01-31",
    "start_period": "2",
    "interest_rate": "1.5"
}
"""