"""
Django models for Accpick Debtor Management System.

This module provides models for customer/debtor account management with clear
separation between:
- User-captured fields (manually entered during account setup)
- System-calculated fields (automatically populated from transactions and month-end processes)
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
import datetime


User = get_user_model()


# ============================================================================
# MANAGERS
# ============================================================================

class DebtorAreaManager(models.Manager):
    """Custom manager for DebtorArea model."""
    
    def with_total_sales(self):
        """Annotate queryset with total sales across all 12 months."""
        from django.db.models import F
        from django.db.models.functions import Coalesce
        
        return self.annotate(
            total_sales=Coalesce(
                F('arsls1') + F('arsls2') + F('arsls3') + F('arsls4') +
                F('arsls5') + F('arsls6') + F('arsls7') + F('arsls8') +
                F('arsls9') + F('arsls10') + F('arsls11') + F('arsls12'),
                Decimal('0.00')
            )
        )


class DebtorManager(models.Manager):
    """Custom manager for Debtor model."""
    
    def active(self):
        """Return only active (non-blocked) debtors."""
        return self.filter(blockflag=False)
    
    def blocked(self):
        """Return only blocked debtors."""
        return self.filter(blockflag=True)
    
    def over_credit_limit(self):
        """Return debtors whose balance exceeds their credit limit."""
        from django.db.models import F
        return self.filter(dposbal__gt=F('dclimit'), dclimit__gt=0)
    
    def with_balances(self):
        """Return debtors with non-zero balances."""
        return self.exclude(dposbal=0)
    
    def zero_balances(self):
        """Return debtors with zero balances."""
        return self.filter(dposbal=0)
    
    def balance_brought_forward(self):
        """Return Balance Brought Forward type debtors."""
        return self.filter(acctype='')
    
    def open_item(self):
        """Return Open Item type debtors."""
        return self.filter(acctype='O')
    
    def cash_type(self):
        """Return Cash type customers."""
        return self.filter(acctype='C')


class DebtorTransactionManager(models.Manager):
    """Custom manager for DebtorTransaction model."""
    
    def for_debtor(self, debtor):
        """Get all transactions for a specific debtor."""
        return self.filter(debtor=debtor).order_by('-dtdate', '-time')
    
    def by_type(self, transaction_type):
        """Filter transactions by type."""
        return self.filter(dtype=transaction_type)
    
    def invoices(self):
        """Get all invoice transactions."""
        return self.filter(dtype='INV')
    
    def credit_notes(self):
        """Get all credit note transactions."""
        return self.filter(dtype='CRN')
    
    def receipts(self):
        """Get all receipt transactions."""
        return self.filter(dtype='RCT')
    
    def cash_sales(self):
        """Get all cash sale transactions."""
        return self.filter(dtype='CSH')
    
    def for_date_range(self, start_date, end_date):
        """Get transactions within a date range."""
        return self.filter(dtdate__gte=start_date, dtdate__lte=end_date)
    
    def current_period(self):
        """Get transactions for current month."""
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        return self.filter(dtdate__gte=start_of_month)


class DebtorOpenManager(models.Manager):
    """Custom manager for DebtorOpen model."""
    
    def for_debtor(self, debtor):
        """Get all open items for a specific debtor."""
        return self.filter(debtor=debtor).order_by('date')
    
    def posted(self):
        """Return only posted items."""
        return self.filter(posted=True)
    
    def unposted(self):
        """Return only unposted items."""
        return self.filter(posted=False)
    
    def outstanding(self):
        """Return items with outstanding balance."""
        return self.exclude(balancedue=0)
    
    def fully_paid(self):
        """Return items that are fully paid."""
        return self.filter(balancedue=0)


# ============================================================================
# MODELS
# ============================================================================

class DebtorArea(models.Model):
    """
    Sales Area / Salesman for categorizing debtors.
    
    Used for performance reporting and sales tracking.
    Monthly sales (arsls1-arsls12) are SYSTEM-CALCULATED during transaction posting.
    """
    # USER-CAPTURED FIELDS
    darea = models.CharField(
        _("Area/Salesman Code"),
        max_length=10,
        primary_key=True,
        help_text=_("Unique identifier for the area/salesman (1-99)")
    )
    dareaname = models.CharField(
        _("Area/Salesman Name"),
        max_length=50,
        help_text=_("Descriptive name for the area or salesman")
    )
    
    # SYSTEM-CALCULATED FIELDS (populated automatically during transaction posting)
    arsls1 = models.DecimalField(_("Sales Month 1"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    arsls2 = models.DecimalField(_("Sales Month 2"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    arsls3 = models.DecimalField(_("Sales Month 3"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    arsls4 = models.DecimalField(_("Sales Month 4"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    arsls5 = models.DecimalField(_("Sales Month 5"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    arsls6 = models.DecimalField(_("Sales Month 6"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    arsls7 = models.DecimalField(_("Sales Month 7"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    arsls8 = models.DecimalField(_("Sales Month 8"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    arsls9 = models.DecimalField(_("Sales Month 9"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    arsls10 = models.DecimalField(_("Sales Month 10"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    arsls11 = models.DecimalField(_("Sales Month 11"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    arsls12 = models.DecimalField(_("Sales Month 12"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)

    objects = DebtorAreaManager()

    class Meta:
        db_table = 'debtor_area'
        verbose_name = _("Sales Area/Salesman")
        verbose_name_plural = _("Sales Areas/Salesmen")
        ordering = ['dareaname']

    def __str__(self):
        return f"{self.darea} - {self.dareaname}"

    def __repr__(self):
        return f"<DebtorArea: {self.darea}>"

    def get_total_sales(self):
        """Calculate total sales across all 12 months."""
        return sum([
            self.arsls1, self.arsls2, self.arsls3, self.arsls4,
            self.arsls5, self.arsls6, self.arsls7, self.arsls8,
            self.arsls9, self.arsls10, self.arsls11, self.arsls12
        ])

    def get_average_monthly_sales(self):
        """Calculate average monthly sales."""
        return self.get_total_sales() / 12


class SalesDepartment(models.Model):
    """
    Sales Department for categorizing stock items and sales.
    
    Used for performance reporting and departmental analysis.
    """
    # USER-CAPTURED FIELDS
    dept_number = models.CharField(
        _("Department Number"),
        max_length=10,
        primary_key=True,
        help_text=_("Department number (1-999)")
    )
    dept_name = models.CharField(
        _("Department Name"),
        max_length=100,
        help_text=_("Descriptive name for the department")
    )
    
    # SYSTEM-CALCULATED FIELDS (populated automatically during transaction posting)
    sales_mtd = models.DecimalField(
        _("Sales Month-to-Date"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False
    )
    sales_ytd = models.DecimalField(
        _("Sales Year-to-Date"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False
    )

    class Meta:
        db_table = 'sales_department'
        verbose_name = _("Sales Department")
        verbose_name_plural = _("Sales Departments")
        ordering = ['dept_name']

    def __str__(self):
        return f"{self.dept_number} - {self.dept_name}"

    def __repr__(self):
        return f"<SalesDepartment: {self.dept_number}>"


class Debtor(models.Model):
    """
    Customer/Debtor Account.
    
    FIELD TYPES:
    1. USER-CAPTURED: Manually entered during account creation/maintenance
    2. SYSTEM-CALCULATED: Automatically populated from transactions and month-end aging
    
    Account Types:
    - Blank = Balance Brought Forward
    - O = Open Item  
    - C = Cash type customer
    """
    
    # Account Type Choices
    ACCOUNT_TYPE_BBF = ''  # Balance Brought Forward
    ACCOUNT_TYPE_OPEN = 'O'  # Open Item
    ACCOUNT_TYPE_CASH = 'C'  # Cash type customer
    
    ACCOUNT_TYPE_CHOICES = [
        (ACCOUNT_TYPE_BBF, _('Balance Brought Forward')),
        (ACCOUNT_TYPE_OPEN, _('Open Item')),
        (ACCOUNT_TYPE_CASH, _('Cash Type Customer')),
    ]
    
    # Terms Choices
    TERMS_CHOICES = [
        ('0', _('0 Days (Cash)')),
        ('7', _('7 Days')),
        ('14', _('14 Days')),
        ('30', _('30 Days')),
        ('60', _('60 Days')),
        ('90', _('90 Days')),
    ]
    
    # Price Level Choices
    PRICE_LEVEL_CHOICES = [
        ('1', _('Price Level 1')),
        ('2', _('Price Level 2')),
        ('3', _('Price Level 3')),
    ]
    
    # ========================================================================
    # USER-CAPTURED FIELDS (entered during account setup/maintenance)
    # ========================================================================
    
    # Primary identification
    dno = models.CharField(
        _("Account Number"),
        max_length=10,
        primary_key=True,
        help_text=_("Unique customer/debtor account number")
    )
    dname = models.CharField(
        _("Name"),
        max_length=50,
        help_text=_("Full customer/company name")
    )
    
    # Postal Address
    dadd1 = models.CharField(_("Address Line 1"), max_length=50, blank=True)
    dadd2 = models.CharField(_("Address Line 2"), max_length=50, blank=True)
    dadd3 = models.CharField(_("Address Line 3"), max_length=50, blank=True)
    dpcode = models.CharField(_("Postal Code"), max_length=10, blank=True)
    
    # Delivery address
    delad1 = models.CharField(_("Delivery Address 1"), max_length=50, blank=True)
    delad2 = models.CharField(_("Delivery Address 2"), max_length=50, blank=True)
    delad3 = models.CharField(_("Delivery Address 3"), max_length=50, blank=True)
    delad4 = models.CharField(_("Delivery Address 4"), max_length=50, blank=True)
    
    # Contact information
    dcontact = models.CharField(
        _("Contact Name"),
        max_length=50,
        blank=True,
        help_text=_("Contact person - appears on Age Analysis with telephone number")
    )
    dtel = models.CharField(_("Tel 1"), max_length=20, blank=True)
    tel2 = models.CharField(_("Tel 2"), max_length=20, blank=True)
    dfax = models.CharField(_("Fax"), max_length=20, blank=True)
    email = models.EmailField(_("Email"), blank=True)
    
    # User/Area/Salesman (captured by logged-in user)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='debtors_created',
        verbose_name=_("Created By"),
        help_text=_("User who created this debtor account")
    )
    darea = models.ForeignKey(
        DebtorArea,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='debtors',
        verbose_name=_("Area/Salesman"),
        help_text=_("Sales area or salesman assigned to this debtor")
    )
    
    # Additional information
    additional_info = models.TextField(
        _("Additional Information"),
        blank=True,
        help_text=_("E.g. Cell number, special notes")
    )
    
    # Discount percentage
    ddiscper = models.DecimalField(
        _("Discount %"),
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        help_text=_("Trade discount % - automatically reduces each line item at POS")
    )
    
    # Credit limit
    dclimit = models.DecimalField(
        _("Credit Limit"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Maximum amount debtor may have outstanding")
    )
    
    # Price code
    price = models.CharField(
        _("Price Code"),
        max_length=10,
        default='1',
        choices=PRICE_LEVEL_CHOICES,
        help_text=_("Price level (1/2/3) - defaults to Level 1")
    )
    
    # Charge interest flag
    dintflag = models.BooleanField(
        _("Charge Interest"),
        default=False,
        help_text=_("Charge interest on overdue accounts")
    )
    
    # Search name
    dsname = models.CharField(
        _("Search Name"),
        max_length=30,
        blank=True,
        help_text=_("Quick access name (usually first 5 characters) for invoicing and enquiries")
    )
    
    # Account category
    acctype = models.CharField(
        _("Account Category"),
        max_length=10,
        blank=True,
        default='',
        choices=ACCOUNT_TYPE_CHOICES,
        help_text=_("Blank=Balance Brought Forward, O=Open Item, C=Cash Customer")
    )
    
    # VAT/Tax reference
    vatref = models.CharField(
        _("VAT/Tax Reference No."),
        max_length=20,
        blank=True,
        help_text=_("SARS VAT Number")
    )
    
    # Terms (payment days)
    terms = models.CharField(
        _("Terms (Days)"),
        max_length=20,
        default='30',
        choices=TERMS_CHOICES,
        help_text=_("Payment terms in days (0 days for Cash type customer)")
    )
    
    # Prompt discount percentage
    pdisc = models.DecimalField(
        _("Prompt Discount %"),
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        help_text=_("% value invoice may be reduced if paid by due date")
    )
    
    # Print on invoices (for prompt discount)
    discprn = models.BooleanField(
        _("Print on Invoices"),
        default=False,
        help_text=_("Print prompt payment discount value and message on invoice")
    )
    
    # Balance on POS documents
    balance_on_pos = models.BooleanField(
        _("Balance on POS Documents"),
        default=True,
        help_text=_("Print credit limit balance on invoices and receipts after each transaction")
    )
    
    # Block status
    blockflag = models.BooleanField(
        _("Change Block Status"),
        default=False,
        help_text=_("When blocked, all transactions are barred")
    )
    
    # Notes
    notes = models.TextField(
        _("Capture Notes"),
        blank=True,
        help_text=_("Additional notes about this debtor")
    )
    
    # ========================================================================
    # SYSTEM-CALCULATED FIELDS (automatically populated by transactions & aging)
    # ========================================================================
    
    # Financial balances - Aging breakdown (populated during month-end aging)
    dbalbfwd = models.DecimalField(
        _("Balance Brought Forward"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        help_text=_("Opening balance at start of period - SYSTEM CALCULATED")
    )
    dcrnt = models.DecimalField(
        _("Current"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        help_text=_("Current month balance - moves to d30 after 30 days during aging - SYSTEM CALCULATED")
    )
    d30 = models.DecimalField(
        _("30 Days"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        help_text=_("30 days aged balance - moves to d60 after aging - SYSTEM CALCULATED")
    )
    d60 = models.DecimalField(
        _("60 Days"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        help_text=_("60 days aged balance - moves to d90 after aging - SYSTEM CALCULATED")
    )
    d90 = models.DecimalField(
        _("90 Days"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        help_text=_("90 days aged balance - moves to d120 after aging - SYSTEM CALCULATED")
    )
    d120 = models.DecimalField(
        _("120 Days"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        help_text=_("120 days aged balance - moves to d150 after aging - SYSTEM CALCULATED")
    )
    d150 = models.DecimalField(
        _("150 Days"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        help_text=_("150 days aged balance - moves to d180 after aging - SYSTEM CALCULATED")
    )
    d180 = models.DecimalField(
        _("180+ Days"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        help_text=_("180+ days aged balance - SYSTEM CALCULATED")
    )
    dposbal = models.DecimalField(
        _("Current Position Balance"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        help_text=_("Total outstanding balance (sum of all aging periods) - SYSTEM CALCULATED")
    )
    
    # Sales and profit tracking (updated during transaction posting)
    dsalesm = models.DecimalField(
        _("Sales Month-to-Date"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        help_text=_("SYSTEM CALCULATED from transactions")
    )
    dsalesy = models.DecimalField(
        _("Sales Year-to-Date"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        help_text=_("SYSTEM CALCULATED from transactions")
    )
    dprofitm = models.DecimalField(
        _("Profit Month-to-Date"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        help_text=_("SYSTEM CALCULATED from transactions")
    )
    dprofity = models.DecimalField(
        _("Profit Year-to-Date"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        help_text=_("SYSTEM CALCULATED from transactions")
    )
    
    # Last payment information (updated during receipt posting)
    damtlpd = models.DecimalField(
        _("Last Payment Amount"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        help_text=_("SYSTEM CALCULATED from last receipt")
    )
    ddatlpd = models.DateField(
        _("Last Payment Date"),
        null=True,
        blank=True,
        editable=False,
        help_text=_("SYSTEM CALCULATED from last receipt")
    )
    
    # Tax number (may be captured or from system)
    dtaxno = models.CharField(
        _("Tax Number"),
        max_length=20,
        blank=True
    )
    
    # Metadata
    dateopened = models.DateField(
        _("Date Opened"),
        auto_now_add=True,
        help_text=_("Date account was created")
    )
    last_modified = models.DateTimeField(
        _("Last Modified"),
        auto_now=True
    )

    objects = DebtorManager()

    class Meta:
        db_table = 'debtor'
        verbose_name = _("Debtor/Customer")
        verbose_name_plural = _("Debtors/Customers")
        ordering = ['dname']
        indexes = [
            models.Index(fields=['dname']),
            models.Index(fields=['dsname']),
            models.Index(fields=['blockflag']),
            models.Index(fields=['darea']),
            models.Index(fields=['dateopened']),
            models.Index(fields=['acctype']),
        ]

    def __str__(self):
        return f"{self.dno} - {self.dname}"

    def __repr__(self):
        return f"<Debtor: {self.dno}>"

    def clean(self):
        """Validate account data."""
        super().clean()
        
        # Cash customers should have 0 day terms
        if self.acctype == self.ACCOUNT_TYPE_CASH and self.terms != '0':
            raise ValidationError({
                'terms': _('Cash type customers must have 0 day terms.')
            })

    def get_total_outstanding(self):
        """
        Calculate total outstanding balance across all aging periods.
        SYSTEM-CALCULATED value.
        """
        return sum([
            self.dcrnt, self.d30, self.d60, self.d90,
            self.d120, self.d150, self.d180
        ])

    def get_overdue_balance(self):
        """
        Calculate total overdue balance (30+ days).
        SYSTEM-CALCULATED value.
        """
        return sum([self.d30, self.d60, self.d90, self.d120, self.d150, self.d180])

    def is_over_credit_limit(self):
        """Check if current balance exceeds credit limit."""
        return self.dposbal > self.dclimit if self.dclimit > 0 else False

    def get_credit_available(self):
        """Calculate available credit remaining."""
        if self.dclimit > 0:
            return max(Decimal('0.00'), self.dclimit - self.dposbal)
        return Decimal('0.00')

    def get_full_address(self):
        """Return formatted full postal address."""
        address_parts = [self.dadd1, self.dadd2, self.dadd3, self.dpcode]
        return ", ".join(filter(None, address_parts))

    def get_delivery_address(self):
        """Return formatted delivery address."""
        address_parts = [self.delad1, self.delad2, self.delad3, self.delad4]
        return ", ".join(filter(None, address_parts))

    def is_balance_brought_forward(self):
        """Check if account is Balance Brought Forward type."""
        return self.acctype == self.ACCOUNT_TYPE_BBF

    def is_open_item(self):
        """Check if account is Open Item type."""
        return self.acctype == self.ACCOUNT_TYPE_OPEN

    def is_cash_customer(self):
        """Check if account is Cash type."""
        return self.acctype == self.ACCOUNT_TYPE_CASH

    def get_gross_profit_margin_mtd(self):
        """Calculate gross profit margin for month-to-date."""
        if self.dsalesm > 0:
            return (self.dprofitm / self.dsalesm) * 100
        return Decimal('0.00')

    def get_gross_profit_margin_ytd(self):
        """Calculate gross profit margin for year-to-date."""
        if self.dsalesy > 0:
            return (self.dprofity / self.dsalesy) * 100
        return Decimal('0.00')

    def update_aging(self):
        """
        Age the balances by moving amounts to next aging period.
        Called during month-end aging process.
        This is a SYSTEM PROCESS - moves dcrnt → d30 → d60 → etc.
        """
        # Move each balance to next aging period
        self.d180 += self.d150
        self.d150 = self.d120
        self.d120 = self.d90
        self.d90 = self.d60
        self.d60 = self.d30
        self.d30 = self.dcrnt
        self.dcrnt = Decimal('0.00')
        
        # Recalculate total position balance
        self.dposbal = self.get_total_outstanding()
        self.save()

    def update_sales_and_profit(self, sales_amount, profit_amount):
        """
        Update MTD and YTD sales and profit figures.
        Called during transaction posting - SYSTEM PROCESS.
        """
        self.dsalesm += sales_amount
        self.dsalesy += sales_amount
        self.dprofitm += profit_amount
        self.dprofity += profit_amount
        self.save()

    def update_last_payment(self, payment_amount, payment_date):
        """
        Update last payment information.
        Called during receipt posting - SYSTEM PROCESS.
        """
        self.damtlpd = payment_amount
        self.ddatlpd = payment_date
        self.save()


class DebtorTransaction(models.Model):
    """
    Financial transaction for a debtor account.
    
    All fields are captured during transaction entry or automatically calculated.
    """
    
    # Transaction Type Choices
    TYPE_INVOICE = 'INV'
    TYPE_CREDIT_NOTE = 'CRN'
    TYPE_CASH_SALE = 'CSH'
    TYPE_CASH_RETURN = 'CSR'
    TYPE_RECEIPT = 'RCT'
    TYPE_SETTLEMENT_DISCOUNT = 'SDC'
    TYPE_INTEREST = 'INT'
    TYPE_DEBIT_JOURNAL = 'DBJ'
    TYPE_CREDIT_JOURNAL = 'CRJ'
    TYPE_LAYBYE = 'LAY'
    
    TRANSACTION_TYPE_CHOICES = [
        (TYPE_INVOICE, _('Invoice')),
        (TYPE_CREDIT_NOTE, _('Credit Note')),
        (TYPE_CASH_SALE, _('Cash Sale')),
        (TYPE_CASH_RETURN, _('Cash Return')),
        (TYPE_RECEIPT, _('Receipt')),
        (TYPE_SETTLEMENT_DISCOUNT, _('Settlement Discount')),
        (TYPE_INTEREST, _('Interest Charge')),
        (TYPE_DEBIT_JOURNAL, _('Debit Journal')),
        (TYPE_CREDIT_JOURNAL, _('Credit Journal')),
        (TYPE_LAYBYE, _('Laybye Sale')),
    ]
    
    debtor = models.ForeignKey(
        Debtor,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_("Debtor")
    )
    dtrano = models.CharField(
        _("Transaction Number"),
        max_length=10,
        help_text=_("Unique transaction number")
    )
    dtdate = models.DateField(_("Transaction Date"))
    time = models.TimeField(_("Transaction Time"), auto_now_add=True)
    dtype = models.CharField(
        _("Transaction Type"),
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES
    )
    dtsub = models.CharField(
        _("Transaction Subtype"),
        max_length=10,
        blank=True
    )
    dtgst = models.DecimalField(
        _("GST/VAT Amount"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    dttot = models.DecimalField(
        _("Transaction Total"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    dtaxstat = models.CharField(
        _("Tax Status"),
        max_length=10,
        blank=True
    )
    source = models.CharField(
        _("Source"),
        max_length=10,
        blank=True
    )
    ordno = models.CharField(
        _("Order Number"),
        max_length=10,
        blank=True
    )
    custref = models.CharField(
        _("Customer Reference"),
        max_length=20,
        blank=True,
        help_text=_("Additional reference/motivation for journals")
    )
    
    # Delivery information
    del1 = models.CharField(_("Delivery Address 1"), max_length=50, blank=True)
    del2 = models.CharField(_("Delivery Address 2"), max_length=50, blank=True)
    del3 = models.CharField(_("Delivery Address 3"), max_length=50, blank=True)
    del4 = models.CharField(_("Delivery Address 4"), max_length=50, blank=True)
    
    # Department tracking
    department = models.ForeignKey(
        SalesDepartment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        verbose_name=_("Sales Department")
    )
    
    # Profit tracking
    cost_price = models.DecimalField(
        _("Cost Price"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    gross_profit = models.DecimalField(
        _("Gross Profit"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions_created',
        verbose_name=_("Created By")
    )

    objects = DebtorTransactionManager()

    class Meta:
        db_table = 'debtor_transaction'
        verbose_name = _("Debtor Transaction")
        verbose_name_plural = _("Debtor Transactions")
        unique_together = [('debtor', 'dtrano')]
        ordering = ['-dtdate', '-time']
        indexes = [
            models.Index(fields=['debtor', 'dtdate']),
            models.Index(fields=['dtype']),
            models.Index(fields=['dtdate']),
            models.Index(fields=['ordno']),
        ]

    def __str__(self):
        return f"{self.debtor.dno} - {self.dtrano} ({self.get_dtype_display()})"

    def __repr__(self):
        return f"<DebtorTransaction: {self.debtor.dno}-{self.dtrano}>"

    def get_net_amount(self):
        """Calculate net amount (total - tax)."""
        return self.dttot - self.dtgst

    def get_delivery_address(self):
        """Return formatted delivery address."""
        address_parts = [self.del1, self.del2, self.del3, self.del4]
        return ", ".join(filter(None, address_parts))

    def get_gross_profit_percentage(self):
        """Calculate gross profit percentage."""
        net_amount = self.get_net_amount()
        if net_amount > 0:
            return (self.gross_profit / net_amount) * 100
        return Decimal('0.00')

    def is_debit_transaction(self):
        """Check if transaction increases debtor balance."""
        return self.dtype in [
            self.TYPE_INVOICE,
            self.TYPE_CASH_SALE,
            self.TYPE_DEBIT_JOURNAL,
            self.TYPE_INTEREST,
            self.TYPE_LAYBYE
        ]

    def is_credit_transaction(self):
        """Check if transaction decreases debtor balance."""
        return self.dtype in [
            self.TYPE_CREDIT_NOTE,
            self.TYPE_CASH_RETURN,
            self.TYPE_RECEIPT,
            self.TYPE_SETTLEMENT_DISCOUNT,
            self.TYPE_CREDIT_JOURNAL
        ]

    def save(self, *args, **kwargs):
        """Override save to update debtor balances."""
        super().save(*args, **kwargs)
        
        # Update debtor's current balance (dcrnt)
        if self.is_debit_transaction():
            self.debtor.dcrnt += self.dttot
        elif self.is_credit_transaction():
            self.debtor.dcrnt -= self.dttot
        
        # Recalculate total position balance
        self.debtor.dposbal = self.debtor.get_total_outstanding()
        
        # Update sales and profit if it's a sales transaction
        if self.dtype in [self.TYPE_INVOICE, self.TYPE_CASH_SALE]:
            self.debtor.update_sales_and_profit(self.get_net_amount(), self.gross_profit)
        
        self.debtor.save()


class DebtorOpen(models.Model):
    """
    Open Item - unpaid or partially paid transaction.
    
    Used for Open Item accounting method.
    System automatically creates/updates during transaction posting.
    """
    
    # Age Flag Choices (aging periods)
    AGE_CURRENT = '1'
    AGE_30_DAYS = '2'
    AGE_60_DAYS = '3'
    AGE_90_DAYS = '4'
    AGE_120_DAYS = '5'
    AGE_150_DAYS = '6'
    AGE_180_DAYS = '7'
    
    AGE_FLAG_CHOICES = [
        (AGE_CURRENT, _('Current')),
        (AGE_30_DAYS, _('30 Days')),
        (AGE_60_DAYS, _('60 Days')),
        (AGE_90_DAYS, _('90 Days')),
        (AGE_120_DAYS, _('120 Days')),
        (AGE_150_DAYS, _('150 Days')),
        (AGE_180_DAYS, _('180+ Days')),
    ]
    
    debtor = models.ForeignKey(
        Debtor,
        on_delete=models.CASCADE,
        related_name='open_items',
        verbose_name=_("Debtor")
    )
    dtrano = models.CharField(
        _("Transaction Number"),
        max_length=10
    )
    type = models.CharField(_("Type"), max_length=10)
    date = models.DateField(_("Date"))
    total = models.DecimalField(
        _("Total Amount"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Original transaction total")
    )
    balancedue = models.DecimalField(
        _("Balance Due"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        help_text=_("Remaining unpaid balance - SYSTEM CALCULATED")
    )
    ageflag = models.CharField(
        _("Age Flag"),
        max_length=10,
        choices=AGE_FLAG_CHOICES,
        default=AGE_CURRENT,
        editable=False,
        help_text=_("Aging period - updated during month-end aging - SYSTEM CALCULATED")
    )
    posted = models.BooleanField(_("Posted"), default=False, editable=False)

    objects = DebtorOpenManager()

    class Meta:
        db_table = 'debtor_open'
        verbose_name = _("Open Item")
        verbose_name_plural = _("Open Items")
        unique_together = [('debtor', 'dtrano')]
        ordering = ['date']
        indexes = [
            models.Index(fields=['debtor', 'posted']),
            models.Index(fields=['ageflag']),
            models.Index(fields=['date']),
            models.Index(fields=['balancedue']),
        ]

    def __str__(self):
        return f"{self.debtor.dno} - {self.dtrano} (Due: {self.balancedue})"

    def __repr__(self):
        return f"<DebtorOpen: {self.debtor.dno}-{self.dtrano}>"

    def is_fully_paid(self):
        """Check if item is fully paid."""
        return self.balancedue == 0

    def get_amount_paid(self):
        """Calculate amount paid (total - balance due)."""
        return self.total - self.balancedue

    def get_payment_percentage(self):
        """Calculate percentage of total amount that has been paid."""
        if self.total == 0:
            return Decimal('0.00')
        return (self.get_amount_paid() / self.total) * 100

    def is_overdue(self):
        """Check if transaction is overdue (not current)."""
        return self.ageflag != self.AGE_CURRENT


class DebtorJournal(models.Model):
    """
    Journal entry for adjustments to debtor accounts.
    
    USER captures: debtor, date, amount, reference, aging allocation
    SYSTEM calculates: updates debtor balances
    """
    
    JOURNAL_TYPE_DEBIT = 'DBJ'
    JOURNAL_TYPE_CREDIT = 'CRJ'
    
    JOURNAL_TYPE_CHOICES = [
        (JOURNAL_TYPE_DEBIT, _('Debit Journal')),
        (JOURNAL_TYPE_CREDIT, _('Credit Journal')),
    ]
    
    debtor = models.ForeignKey(
        Debtor,
        on_delete=models.CASCADE,
        related_name='journals',
        verbose_name=_("Debtor")
    )
    journal_no = models.CharField(
        _("Journal Number"),
        max_length=10,
        unique=True,
        help_text=_("Unique journal number - consecutive sequence")
    )
    journal_type = models.CharField(
        _("Journal Type"),
        max_length=10,
        choices=JOURNAL_TYPE_CHOICES
    )
    date = models.DateField(_("Journal Date"))
    amount = models.DecimalField(
        _("Journal Amount"),
        max_digits=12,
        decimal_places=2
    )
    reference = models.CharField(
        _("Additional Reference"),
        max_length=100,
        help_text=_("Short explanation - appears on statement and reports")
    )
    
    # Aging allocation for Balance Brought Forward
    age_current = models.DecimalField(_("Current"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    age_30 = models.DecimalField(_("30 Days"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    age_60 = models.DecimalField(_("60 Days"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    age_90 = models.DecimalField(_("90 Days"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    age_120 = models.DecimalField(_("120 Days"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    age_150 = models.DecimalField(_("150 Days"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    age_180 = models.DecimalField(_("180+ Days"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # For Open Item - single aging period
    ageflag = models.CharField(
        _("Age Flag"),
        max_length=10,
        blank=True,
        help_text=_("For Open Item accounts - single aging period")
    )
    
    posted = models.BooleanField(_("Posted"), default=False)
    batch_no = models.CharField(_("Batch Number"), max_length=10, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Created By")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'debtor_journal'
        verbose_name = _("Debtor Journal")
        verbose_name_plural = _("Debtor Journals")
        ordering = ['-date', '-journal_no']
        indexes = [
            models.Index(fields=['debtor', 'date']),
            models.Index(fields=['journal_type']),
            models.Index(fields=['batch_no']),
        ]

    def __str__(self):
        return f"{self.journal_no} - {self.debtor.dno} ({self.get_journal_type_display()})"

    def clean(self):
        """Validate journal entry."""
        super().clean()
        
        # For Balance Brought Forward, aging must balance with amount
        if self.debtor and self.debtor.is_balance_brought_forward():
            total_aging = sum([
                self.age_current, self.age_30, self.age_60, self.age_90,
                self.age_120, self.age_150, self.age_180
            ])
            if abs(total_aging - abs(self.amount)) > Decimal('0.01'):
                raise ValidationError({
                    'amount': _('Aging total must balance with journal amount.')
                })


class PostDatedCheque(models.Model):
    """
    Post-dated cheque (PDC) for information purposes.
    
    USER captures: debtor, cheque_date, amount, cheque details
    SYSTEM manages: processed flag, reminders
    """
    debtor = models.ForeignKey(
        Debtor,
        on_delete=models.CASCADE,
        related_name='post_dated_cheques',
        verbose_name=_("Debtor")
    )
    cheque_date = models.DateField(
        _("Cheque Date"),
        help_text=_("Date cheque becomes valid")
    )
    amount = models.DecimalField(
        _("Cheque Amount"),
        max_digits=12,
        decimal_places=2
    )
    cheque_number = models.CharField(_("Cheque Number"), max_length=20, blank=True)
    bank_name = models.CharField(_("Bank Name"), max_length=50, blank=True)
    
    # System fields
    captured_date = models.DateField(_("Captured Date"), auto_now_add=True, editable=False)
    processed = models.BooleanField(_("Processed"), default=False, editable=False)
    cancelled = models.BooleanField(_("Cancelled"), default=False)
    notes = models.TextField(_("Notes"), blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Created By")
    )

    class Meta:
        db_table = 'post_dated_cheque'
        verbose_name = _("Post-Dated Cheque")
        verbose_name_plural = _("Post-Dated Cheques")
        ordering = ['cheque_date', 'debtor']
        indexes = [
            models.Index(fields=['cheque_date', 'processed']),
            models.Index(fields=['debtor']),
        ]

    def __str__(self):
        return f"{self.debtor.dno} - {self.amount} on {self.cheque_date}"

    def is_due_today(self):
        """Check if cheque is due today."""
        return self.cheque_date == timezone.now().date()

    def is_due_tomorrow(self):
        """Check if cheque is due tomorrow."""
        tomorrow = timezone.now().date() + datetime.timedelta(days=1)
        return self.cheque_date == tomorrow

    def is_overdue(self):
        """Check if cheque date has passed."""
        return self.cheque_date < timezone.now().date() and not self.processed


class InterestCharge(models.Model):
    """
    Interest charge applied to overdue debtor accounts.
    
    Applied at month end - SYSTEM PROCESS
    """
    charge_date = models.DateField(
        _("Interest Charge Date"),
        help_text=_("Date interest is charged - usually month end")
    )
    debtor = models.ForeignKey(
        Debtor,
        on_delete=models.CASCADE,
        related_name='interest_charges',
        verbose_name=_("Debtor")
    )
    start_period = models.CharField(
        _("Start Charging At"),
        max_length=10,
        help_text=_("Period from which to charge (1=Current, 2=30 days, etc.)")
    )
    interest_rate = models.DecimalField(
        _("Monthly Interest Rate %"),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))]
    )
    balance_charged = models.DecimalField(
        _("Balance Charged"),
        max_digits=12,
        decimal_places=2,
        editable=False,
        help_text=_("SYSTEM CALCULATED")
    )
    interest_amount = models.DecimalField(
        _("Interest Amount"),
        max_digits=12,
        decimal_places=2,
        editable=False,
        help_text=_("SYSTEM CALCULATED")
    )
    posted = models.BooleanField(_("Posted"), default=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'interest_charge'
        verbose_name = _("Interest Charge")
        verbose_name_plural = _("Interest Charges")
        ordering = ['-charge_date', 'debtor']
        indexes = [
            models.Index(fields=['charge_date']),
            models.Index(fields=['debtor', 'charge_date']),
        ]

    def __str__(self):
        return f"{self.debtor.dno} - {self.interest_amount} on {self.charge_date}"


class ReceiptAllocation(models.Model):
    """
    Allocation of receipt payment to specific open items.
    
    For Open Item accounts - tracks which invoices a payment was applied to.
    SYSTEM creates during receipt posting.
    """
    receipt_transaction = models.ForeignKey(
        DebtorTransaction,
        on_delete=models.CASCADE,
        related_name='allocations',
        verbose_name=_("Receipt Transaction")
    )
    open_item = models.ForeignKey(
        DebtorOpen,
        on_delete=models.CASCADE,
        related_name='allocations',
        verbose_name=_("Open Item")
    )
    amount_paid = models.DecimalField(
        _("Amount Paid"),
        max_digits=12,
        decimal_places=2
    )
    settlement_discount = models.DecimalField(
        _("Settlement Discount"),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    fully_paid = models.BooleanField(
        _("Fully Paid"),
        default=False,
        help_text=_("Marked with * if balance due paid in full")
    )
    allocation_date = models.DateField(_("Allocation Date"))
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        db_table = 'receipt_allocation'
        verbose_name = _("Receipt Allocation")
        verbose_name_plural = _("Receipt Allocations")
        ordering = ['-allocation_date']
        indexes = [
            models.Index(fields=['receipt_transaction']),
            models.Index(fields=['open_item']),
        ]

    def __str__(self):
        return f"{self.receipt_transaction.dtrano} -> {self.open_item.dtrano}: {self.amount_paid}"

    def clean(self):
        """Validate allocation."""
        super().clean()
        
        if self.receipt_transaction.debtor != self.open_item.debtor:
            raise ValidationError(_('Receipt and open item must be for same debtor.'))
        
        if not self.fully_paid and self.settlement_discount > 0:
            raise ValidationError({
                'settlement_discount': _('No settlement discount allowed on part payments.')
            })

    def save(self, *args, **kwargs):
        """Override save to update open item balance."""
        super().save(*args, **kwargs)
        
        # Update the open item's balance due
        self.open_item.balancedue -= (self.amount_paid + self.settlement_discount)
        self.open_item.save()