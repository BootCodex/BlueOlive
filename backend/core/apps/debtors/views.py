"""
Django REST Framework views for Accpick Debtor Management System.

Provides ViewSets and APIViews for all models with filtering, searching,
pagination, and custom actions for business logic.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, F
from django.utils import timezone
from decimal import Decimal
import datetime
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import (
    DebtorArea,
    SalesDepartment,
    Debtor,
    DebtorTransaction,
    DebtorOpen,
    DebtorJournal,
    PostDatedCheque,
    InterestCharge,
    ReceiptAllocation
)
from .serializers import (
    DebtorAreaSerializer,
    SalesDepartmentSerializer,
    DebtorSerializer,
    DebtorListSerializer,
    DebtorTransactionSerializer,
    DebtorOpenSerializer,
    DebtorJournalSerializer,
    PostDatedChequeSerializer,
    InterestChargeSerializer,
    ReceiptAllocationSerializer,
    DebtorAgingSummarySerializer,
    DebtorPerformanceSerializer,
)


# ============================================================================
# DEBTOR AREA / SALESMAN VIEWSET
# ============================================================================

class DebtorAreaViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Sales Areas / Salesmen.
    
    list: Get all areas/salesmen
    retrieve: Get specific area/salesman
    create: Create new area/salesman
    update: Update area/salesman
    delete: Delete area/salesman
    
    Custom actions:
    - sales_performance: Get sales performance for area
    - debtors: Get all debtors in area
    """
    
    queryset = DebtorArea.objects.all()
    serializer_class = DebtorAreaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['darea', 'dareaname']
    ordering_fields = ['darea', 'dareaname']
    ordering = ['dareaname']
    
    @action(detail=True, methods=['get'])
    def sales_performance(self, request, pk=None):
        """Get sales performance for this area."""
        area = self.get_object()
        
        performance_data = {
            'area_code': area.darea,
            'area_name': area.dareaname,
            'total_sales': area.get_total_sales(),
            'average_monthly_sales': area.get_average_monthly_sales(),
            'monthly_breakdown': {
                'month_1': area.arsls1,
                'month_2': area.arsls2,
                'month_3': area.arsls3,
                'month_4': area.arsls4,
                'month_5': area.arsls5,
                'month_6': area.arsls6,
                'month_7': area.arsls7,
                'month_8': area.arsls8,
                'month_9': area.arsls9,
                'month_10': area.arsls10,
                'month_11': area.arsls11,
                'month_12': area.arsls12,
            },
            'debtor_count': area.debtors.count(),
            'active_debtors': area.debtors.filter(blockflag=False).count(),
        }
        
        return Response(performance_data)
    
    @action(detail=True, methods=['get'])
    def debtors(self, request, pk=None):
        """Get all debtors in this area."""
        area = self.get_object()
        debtors = area.debtors.all()
        serializer = DebtorListSerializer(debtors, many=True)
        return Response(serializer.data)


# ============================================================================
# SALES DEPARTMENT VIEWSET
# ============================================================================

class SalesDepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Sales Departments.
    
    list: Get all departments
    retrieve: Get specific department
    create: Create new department
    update: Update department
    delete: Delete department
    
    Custom actions:
    - sales_performance: Get sales performance for department
    """
    
    queryset = SalesDepartment.objects.all()
    serializer_class = SalesDepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['dept_number', 'dept_name']
    ordering_fields = ['dept_number', 'dept_name', 'sales_mtd', 'sales_ytd']
    ordering = ['dept_name']
    
    @action(detail=True, methods=['get'])
    def sales_performance(self, request, pk=None):
        """Get sales performance for this department."""
        department = self.get_object()
        
        performance_data = {
            'dept_number': department.dept_number,
            'dept_name': department.dept_name,
            'sales_mtd': department.sales_mtd,
            'sales_ytd': department.sales_ytd,
            'transaction_count': department.transactions.count(),
        }
        
        return Response(performance_data)


# ============================================================================
# DEBTOR VIEWSET
# ============================================================================

class DebtorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Debtors/Customers.
    
    list: Get all debtors (uses lightweight serializer)
    retrieve: Get specific debtor (full details)
    create: Create new debtor
    update: Update debtor
    delete: Delete debtor
    
    Filters:
    - blockflag: Filter by blocked status
    - acctype: Filter by account type
    - darea: Filter by area/salesman
    
    Custom actions:
    - transactions: Get all transactions for debtor
    - open_items: Get all open items for debtor
    - age_analysis: Get aging analysis for debtor
    - statement: Generate statement for debtor
    - over_credit_limit: Get debtors over credit limit
    - blocked_accounts: Get blocked accounts
    """
    
    queryset = Debtor.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['blockflag', 'acctype', 'darea']
    search_fields = ['dno', 'dname', 'dsname', 'dtel', 'email']
    ordering_fields = ['dno', 'dname', 'dposbal', 'dclimit', 'dateopened']
    ordering = ['dname']
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view."""
        if self.action == 'list':
            return DebtorListSerializer
        return DebtorSerializer
    
    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def over_credit_limit(self, request):
        """Get all debtors over their credit limit."""
        debtors = Debtor.objects.over_credit_limit()
        serializer = DebtorListSerializer(debtors, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def blocked_accounts(self, request):
        """Get all blocked accounts."""
        debtors = Debtor.objects.blocked()
        serializer = DebtorListSerializer(debtors, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def with_balances(self, request):
        """Get all debtors with non-zero balances."""
        debtors = Debtor.objects.with_balances()
        serializer = DebtorListSerializer(debtors, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Get all transactions for this debtor."""
        debtor = self.get_object()
        transactions = debtor.transactions.all()
        
        # Optional date filtering
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            transactions = transactions.filter(dtdate__gte=start_date)
        if end_date:
            transactions = transactions.filter(dtdate__lte=end_date)
        
        serializer = DebtorTransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def open_items(self, request, pk=None):
        """Get all open items for this debtor."""
        debtor = self.get_object()
        
        if not debtor.is_open_item():
            return Response(
                {'error': 'This debtor is not an Open Item account.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        open_items = debtor.open_items.outstanding()
        serializer = DebtorOpenSerializer(open_items, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def age_analysis(self, request, pk=None):
        """Get aging analysis for this debtor."""
        debtor = self.get_object()
        
        aging_data = {
            'dno': debtor.dno,
            'dname': debtor.dname,
            'dcontact': debtor.dcontact,
            'dtel': debtor.dtel,
            'current': debtor.dcrnt,
            'days_30': debtor.d30,
            'days_60': debtor.d60,
            'days_90': debtor.d90,
            'days_120': debtor.d120,
            'days_150': debtor.d150,
            'days_180': debtor.d180,
            'total_outstanding': debtor.get_total_outstanding(),
            'credit_limit': debtor.dclimit,
            'credit_available': debtor.get_credit_available(),
            'overdue_balance': debtor.get_overdue_balance(),
            'is_over_credit_limit': debtor.is_over_credit_limit(),
        }
        
        return Response(aging_data)
    
    @action(detail=True, methods=['get'])
    def statement(self, request, pk=None):
        """Generate statement for this debtor."""
        debtor = self.get_object()
        
        # Get date range from query params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Default to current month if not specified
        if not start_date:
            today = timezone.now().date()
            start_date = today.replace(day=1)
        if not end_date:
            end_date = timezone.now().date()
        
        # Get transactions
        transactions = debtor.transactions.filter(
            dtdate__gte=start_date,
            dtdate__lte=end_date
        ).order_by('dtdate', 'time')
        
        statement_data = {
            'debtor': DebtorSerializer(debtor).data,
            'statement_period': {
                'start_date': start_date,
                'end_date': end_date,
            },
            'opening_balance': debtor.dbalbfwd,
            'transactions': DebtorTransactionSerializer(transactions, many=True).data,
            'closing_balance': debtor.dposbal,
            'aging': {
                'current': debtor.dcrnt,
                '30_days': debtor.d30,
                '60_days': debtor.d60,
                '90_days': debtor.d90,
                '120_days': debtor.d120,
                '150_days': debtor.d150,
                '180_days': debtor.d180,
            }
        }
        
        return Response(statement_data)
    
    @action(detail=True, methods=['post'])
    def update_aging(self, request, pk=None):
        """
        Manually trigger aging update for this debtor.
        (Normally done during month-end process)
        """
        debtor = self.get_object()
        debtor.update_aging()
        
        return Response({
            'message': 'Aging updated successfully',
            'aging': {
                'current': debtor.dcrnt,
                '30_days': debtor.d30,
                '60_days': debtor.d60,
                '90_days': debtor.d90,
                '120_days': debtor.d120,
                '150_days': debtor.d150,
                '180_days': debtor.d180,
                'total': debtor.dposbal,
            }
        })


# ============================================================================
# DEBTOR TRANSACTION VIEWSET
# ============================================================================

class DebtorTransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Debtor Transactions.
    
    list: Get all transactions
    retrieve: Get specific transaction
    create: Create new transaction
    update: Update transaction
    delete: Delete transaction
    
    Filters:
    - debtor: Filter by debtor
    - dtype: Filter by transaction type
    - dtdate: Filter by transaction date
    
    Custom actions:
    - by_type: Get transactions by type
    - current_period: Get current month transactions
    - gross_profit_report: Get gross profit report
    """
    
    queryset = DebtorTransaction.objects.all()
    serializer_class = DebtorTransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['debtor', 'dtype', 'dtdate', 'department']
    search_fields = ['dtrano', 'ordno', 'custref']
    ordering_fields = ['dtdate', 'time', 'dttot']
    ordering = ['-dtdate', '-time']
    
    def perform_create(self, serializer):
        """Set created_by to current user and auto-generate transaction number."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get transactions filtered by type."""
        dtype = request.query_params.get('type')
        
        if not dtype:
            return Response(
                {'error': 'Transaction type parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transactions = self.queryset.filter(dtype=dtype)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def current_period(self, request):
        """Get transactions for current month."""
        transactions = DebtorTransaction.objects.current_period()
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def gross_profit_report(self, request):
        """Get gross profit report for date range."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        transactions = self.queryset.filter(
            dtype__in=[
                DebtorTransaction.TYPE_INVOICE,
                DebtorTransaction.TYPE_CASH_SALE
            ]
        )
        
        if start_date:
            transactions = transactions.filter(dtdate__gte=start_date)
        if end_date:
            transactions = transactions.filter(dtdate__lte=end_date)
        
        # Calculate totals
        totals = transactions.aggregate(
            total_sales=Sum('dttot'),
            total_cost=Sum('cost_price'),
            total_profit=Sum('gross_profit'),
        )
        
        gp_percentage = 0
        if totals['total_sales']:
            gp_percentage = (totals['total_profit'] / totals['total_sales']) * 100
        
        report_data = {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
            },
            'totals': {
                'sales': totals['total_sales'] or 0,
                'cost': totals['total_cost'] or 0,
                'profit': totals['total_profit'] or 0,
                'gp_percentage': gp_percentage,
            },
            'transaction_count': transactions.count(),
        }
        
        return Response(report_data)


# ============================================================================
# DEBTOR OPEN VIEWSET
# ============================================================================

class DebtorOpenViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Debtor Open Items.
    
    list: Get all open items
    retrieve: Get specific open item
    create: Create new open item
    update: Update open item
    delete: Delete open item
    
    Filters:
    - debtor: Filter by debtor
    - posted: Filter by posted status
    - ageflag: Filter by aging period
    
    Custom actions:
    - outstanding: Get outstanding open items
    - aged_report: Get aged open items report
    """
    
    queryset = DebtorOpen.objects.all()
    serializer_class = DebtorOpenSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['debtor', 'posted', 'ageflag', 'type']
    search_fields = ['dtrano']
    ordering_fields = ['date', 'balancedue']
    ordering = ['date']
    
    @action(detail=False, methods=['get'])
    def outstanding(self, request):
        """Get all outstanding open items."""
        items = DebtorOpen.objects.outstanding()
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def aged_report(self, request):
        """Get aged open items report grouped by aging period."""
        items = DebtorOpen.objects.outstanding()
        
        aged_summary = {}
        for age_choice in DebtorOpen.AGE_FLAG_CHOICES:
            age_code, age_label = age_choice
            age_items = items.filter(ageflag=age_code)
            
            aged_summary[age_label] = {
                'count': age_items.count(),
                'total_balance': float(age_items.aggregate(
                    total=Sum('balancedue')
                )['total'] or 0)
            }
        
        return Response(aged_summary)


# ============================================================================
# DEBTOR JOURNAL VIEWSET
# ============================================================================

class DebtorJournalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Debtor Journals.
    
    list: Get all journals
    retrieve: Get specific journal
    create: Create new journal
    update: Update journal
    delete: Delete journal
    
    Filters:
    - debtor: Filter by debtor
    - journal_type: Filter by journal type (debit/credit)
    - posted: Filter by posted status
    - batch_no: Filter by batch number
    """
    
    queryset = DebtorJournal.objects.all()
    serializer_class = DebtorJournalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['debtor', 'journal_type', 'posted', 'batch_no']
    search_fields = ['journal_no', 'reference']
    ordering_fields = ['date', 'journal_no', 'amount']
    ordering = ['-date', '-journal_no']
    
    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def post_batch(self, request):
        """Post a batch of journals."""
        batch_no = request.data.get('batch_no')
        
        if not batch_no:
            return Response(
                {'error': 'Batch number is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        journals = self.queryset.filter(batch_no=batch_no, posted=False)
        
        if not journals.exists():
            return Response(
                {'error': 'No unposted journals found for this batch.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Post all journals in batch
        posted_count = journals.update(posted=True)
        
        return Response({
            'message': f'Successfully posted {posted_count} journals',
            'batch_no': batch_no,
        })


# ============================================================================
# POST DATED CHEQUE VIEWSET
# ============================================================================

class PostDatedChequeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Post-Dated Cheques.
    
    list: Get all PDCs
    retrieve: Get specific PDC
    create: Create new PDC
    update: Update PDC
    delete: Delete PDC
    
    Custom actions:
    - due_today: Get PDCs due today
    - due_tomorrow: Get PDCs due tomorrow
    - overdue: Get overdue PDCs
    - process: Mark PDC as processed
    - cancel: Mark PDC as cancelled
    """
    
    queryset = PostDatedCheque.objects.all()
    serializer_class = PostDatedChequeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['debtor', 'processed', 'cancelled']
    search_fields = ['cheque_number', 'bank_name']
    ordering_fields = ['cheque_date', 'amount']
    ordering = ['cheque_date']
    
    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def due_today(self, request):
        """Get all PDCs due today."""
        today = timezone.now().date()
        cheques = self.queryset.filter(
            cheque_date=today,
            processed=False,
            cancelled=False
        )
        serializer = self.get_serializer(cheques, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def due_tomorrow(self, request):
        """Get all PDCs due tomorrow."""
        tomorrow = timezone.now().date() + datetime.timedelta(days=1)
        cheques = self.queryset.filter(
            cheque_date=tomorrow,
            processed=False,
            cancelled=False
        )
        serializer = self.get_serializer(cheques, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue PDCs."""
        today = timezone.now().date()
        cheques = self.queryset.filter(
            cheque_date__lt=today,
            processed=False,
            cancelled=False
        )
        serializer = self.get_serializer(cheques, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Mark PDC as processed."""
        cheque = self.get_object()
        cheque.processed = True
        cheque.save()
        
        return Response({
            'message': 'Cheque marked as processed',
            'cheque': self.get_serializer(cheque).data
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Mark PDC as cancelled."""
        cheque = self.get_object()
        cheque.cancelled = True
        cheque.save()
        
        return Response({
            'message': 'Cheque marked as cancelled',
            'cheque': self.get_serializer(cheque).data
        })


# ============================================================================
# INTEREST CHARGE VIEWSET
# ============================================================================

class InterestChargeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Interest Charges.
    
    list: Get all interest charges
    retrieve: Get specific interest charge
    create: Create new interest charge
    
    Custom actions:
    - calculate_interest: Calculate interest for eligible debtors
    """
    
    queryset = InterestCharge.objects.all()
    serializer_class = InterestChargeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['debtor', 'posted', 'charge_date']
    ordering_fields = ['charge_date', 'interest_amount']
    ordering = ['-charge_date']
    
    @action(detail=False, methods=['post'])
    def calculate_interest(self, request):
        """
        Calculate interest for all eligible debtors.
        
        Expected params:
        - charge_date: Date to charge interest
        - start_period: Period from which to start charging (1-7)
        - interest_rate: Monthly interest rate percentage
        - pay_on_credit: Whether to pay interest on credit balances
        """
        charge_date = request.data.get('charge_date', timezone.now().date())
        start_period = request.data.get('start_period', '2')  # Default to 30 days
        interest_rate = Decimal(request.data.get('interest_rate', '0'))
        pay_on_credit = request.data.get('pay_on_credit', False)
        
        if interest_rate <= 0:
            return Response(
                {'error': 'Interest rate must be greater than 0.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get debtors eligible for interest
        debtors = Debtor.objects.filter(dintflag=True, blockflag=False)
        
        charges_created = []
        total_interest = Decimal('0.00')
        
        for debtor in debtors:
            # Calculate balance to charge based on start period
            balance_to_charge = Decimal('0.00')
            
            if start_period == '1':  # From current
                balance_to_charge = debtor.get_total_outstanding()
            elif start_period == '2':  # From 30 days
                balance_to_charge = debtor.get_overdue_balance()
            # Add more period logic as needed
            
            if balance_to_charge > 0 or (pay_on_credit and balance_to_charge < 0):
                interest_amount = (abs(balance_to_charge) * interest_rate) / 100
                
                charge = InterestCharge.objects.create(
                    charge_date=charge_date,
                    debtor=debtor,
                    start_period=start_period,
                    interest_rate=interest_rate,
                    balance_charged=balance_to_charge,
                    interest_amount=interest_amount,
                    posted=False,
                )
                
                charges_created.append(charge)
                total_interest += interest_amount
        
        return Response({
            'message': f'Interest calculated for {len(charges_created)} debtors',
            'total_interest': float(total_interest),
            'charges': InterestChargeSerializer(charges_created, many=True).data,
        })


# ============================================================================
# RECEIPT ALLOCATION VIEWSET
# ============================================================================

class ReceiptAllocationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Receipt Allocations.
    
    list: Get all allocations
    retrieve: Get specific allocation
    create: Create new allocation
    update: Update allocation
    delete: Delete allocation
    """
    
    queryset = ReceiptAllocation.objects.all()
    serializer_class = ReceiptAllocationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['receipt_transaction', 'open_item', 'fully_paid']
    ordering_fields = ['allocation_date', 'amount_paid']
    ordering = ['-allocation_date']


# ============================================================================
# HTML VIEWS
# ============================================================================

class BaseDebtorView(LoginRequiredMixin, TemplateView):
    """Base view for debtor templates."""
    pass


class DashboardView(BaseDebtorView):
    """Dashboard view with statistics and recent activity."""
    template_name = 'debtors/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Statistics
        context['total_debtors'] = Debtor.objects.count()
        context['total_outstanding'] = Debtor.objects.aggregate(total=Sum('dposbal'))['total'] or 0
        context['overdue_accounts'] = Debtor.objects.filter(d30__gt=0).count()

        # Current month sales
        now = timezone.now()
        context['current_month_sales'] = DebtorTransaction.objects.filter(
            dtype__in=['INV', 'CSH'],
            dtdate__year=now.year,
            dtdate__month=now.month
        ).aggregate(total=Sum('dttot'))['total'] or 0

        # Recent transactions
        context['recent_transactions'] = DebtorTransaction.objects.select_related('debtor').order_by('-dtdate', '-time')[:5]

        # Overdue accounts
        context['overdue_list'] = Debtor.objects.filter(d30__gt=0).order_by('-d30')[:5]

        # Upcoming PDCs
        context['upcoming_pdcs'] = PostDatedCheque.objects.select_related('debtor').filter(
            processed=False,
            cancelled=False,
            cheque_date__gte=timezone.now().date()
        ).order_by('cheque_date')[:5]

        # Age analysis data for chart
        context['age_analysis_data'] = [
            Debtor.objects.aggregate(sum=Sum('dcrnt'))['sum'] or 0,
            Debtor.objects.aggregate(sum=Sum('d30'))['sum'] or 0,
            Debtor.objects.aggregate(sum=Sum('d60'))['sum'] or 0,
            Debtor.objects.aggregate(sum=Sum('d90'))['sum'] or 0,
            Debtor.objects.aggregate(sum=Sum('d120'))['sum'] or 0,
            Debtor.objects.aggregate(sum=Sum('d150'))['sum'] or 0,
            Debtor.objects.aggregate(sum=Sum('d180'))['sum'] or 0,
        ]

        return context


class AccountListView(BaseDebtorView, ListView):
    """List all debtor accounts."""
    template_name = 'debtors/account_list.html'
    model = Debtor
    context_object_name = 'debtors'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        # Add filters based on query params
        blockflag = self.request.GET.get('blockflag')
        acctype = self.request.GET.get('acctype')
        search = self.request.GET.get('search')

        if blockflag:
            queryset = queryset.filter(blockflag=blockflag.lower() == 'true')
        if acctype:
            queryset = queryset.filter(acctype=acctype)
        if search:
            queryset = queryset.filter(
                Q(dno__icontains=search) |
                Q(dname__icontains=search) |
                Q(dsname__icontains=search) |
                Q(dtel__icontains=search) |
                Q(email__icontains=search)
            )

        return queryset.order_by('dname')


class AccountDetailView(BaseDebtorView, DetailView):
    """View details of a specific debtor account."""
    template_name = 'debtors/account_detail.html'
    model = Debtor
    context_object_name = 'debtor'


class AccountCreateView(BaseDebtorView, CreateView):
    """Create a new debtor account."""
    template_name = 'debtors/account_form.html'
    model = Debtor
    fields = ['dno', 'dname', 'dsname', 'dadd1', 'dadd2', 'dadd3', 'dpcode',
              'dcontact', 'dtel', 'tel2', 'dfax', 'email', 'darea', 'additional_info',
              'ddiscper', 'dclimit', 'price', 'dintflag', 'dsname', 'acctype',
              'vatref', 'terms', 'pdisc', 'discprn', 'balance_on_pos', 'blockflag', 'notes']
    success_url = reverse_lazy('debtors:account_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class AccountUpdateView(BaseDebtorView, UpdateView):
    """Update an existing debtor account."""
    template_name = 'debtors/account_form.html'
    model = Debtor
    fields = ['dno', 'dname', 'dsname', 'dadd1', 'dadd2', 'dadd3', 'dpcode',
              'dcontact', 'dtel', 'tel2', 'dfax', 'email', 'darea', 'additional_info',
              'ddiscper', 'dclimit', 'price', 'dintflag', 'dsname', 'acctype',
              'vatref', 'terms', 'pdisc', 'discprn', 'balance_on_pos', 'blockflag', 'notes']
    success_url = reverse_lazy('debtors:account_list')


class TransactionListView(BaseDebtorView, ListView):
    """List all debtor transactions."""
    template_name = 'debtors/transaction_list.html'
    model = DebtorTransaction
    context_object_name = 'transactions'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset().select_related('debtor')
        # Add filters
        debtor = self.request.GET.get('debtor')
        dtype = self.request.GET.get('dtype')
        search = self.request.GET.get('search')

        if debtor:
            queryset = queryset.filter(debtor__dno=debtor)
        if dtype:
            queryset = queryset.filter(dtype=dtype)
        if search:
            queryset = queryset.filter(
                Q(dtrano__icontains=search) |
                Q(ordno__icontains=search) |
                Q(custref__icontains=search)
            )

        return queryset.order_by('-dtdate', '-time')


class AgeAnalysisView(BaseDebtorView):
    """Age analysis report."""
    template_name = 'debtors/age_analysis.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all debtors with balances
        debtors = Debtor.objects.with_balances().order_by('-dposbal')

        # Calculate totals
        context['total_current'] = sum(d.dcrnt for d in debtors)
        context['total_30'] = sum(d.d30 for d in debtors)
        context['total_60'] = sum(d.d60 for d in debtors)
        context['total_90'] = sum(d.d90 for d in debtors)
        context['total_120'] = sum(d.d120 for d in debtors)
        context['total_150'] = sum(d.d150 for d in debtors)
        context['total_180'] = sum(d.d180 for d in debtors)
        context['grand_total'] = context['total_current'] + context['total_30'] + context['total_60'] + context['total_90'] + context['total_120'] + context['total_150'] + context['total_180']

        context['debtors'] = debtors

        return context


class DebitJournalView(BaseDebtorView):
    """Debit journal entry."""
    template_name = 'debtors/debit_journal.html'


class CreditJournalView(BaseDebtorView):
    """Credit journal entry."""
    template_name = 'debtors/credit_journal.html'


class BatchReceiptView(BaseDebtorView):
    """Batch receipt entry."""
    template_name = 'debtors/batch_receipt.html'


class PDCListView(BaseDebtorView, ListView):
    """List post-dated cheques."""
    template_name = 'debtors/pdc_list.html'
    model = PostDatedCheque
    context_object_name = 'pdcs'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset().select_related('debtor')
        processed = self.request.GET.get('processed')
        cancelled = self.request.GET.get('cancelled')
        search = self.request.GET.get('search')

        if processed:
            queryset = queryset.filter(processed=processed.lower() == 'true')
        if cancelled:
            queryset = queryset.filter(cancelled=cancelled.lower() == 'true')
        if search:
            queryset = queryset.filter(
                Q(cheque_number__icontains=search) |
                Q(bank_name__icontains=search) |
                Q(debtor__dno__icontains=search) |
                Q(debtor__dname__icontains=search)
            )

        return queryset.order_by('cheque_date')


class InterestChargingView(BaseDebtorView):
    """Interest charging interface."""
    template_name = 'debtors/interest_charging.html'


class ReportsView(BaseDebtorView):
    """Reports menu."""
    template_name = 'debtors/reports_menu.html'


class SalesAreasListView(BaseDebtorView, ListView):
    """List sales areas."""
    template_name = 'debtors/sales_areas_list.html'
    model = DebtorArea
    context_object_name = 'areas'
    paginate_by = 25


class DepartmentsListView(BaseDebtorView, ListView):
    """List departments."""
    template_name = 'debtors/departments_list.html'
    model = SalesDepartment
    context_object_name = 'departments'
    paginate_by = 25


class AccountBalancesView(BaseDebtorView, ListView):
    """Account balances report."""
    template_name = 'debtors/account_balances.html'
    model = Debtor
    context_object_name = 'debtors'
    paginate_by = 50

    def get_queryset(self):
        return Debtor.objects.with_balances().order_by('-dposbal')


class TopAccountsView(BaseDebtorView, ListView):
    """Top accounts by sales."""
    template_name = 'debtors/top_accounts.html'
    model = Debtor
    context_object_name = 'debtors'
    paginate_by = 25

    def get_queryset(self):
        return Debtor.objects.order_by('-dsalesy')[:100]


class IndividualAccountView(BaseDebtorView):
    """Individual account enquiry."""
    template_name = 'debtors/individual_account.html'