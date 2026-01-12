"""
Django REST Framework serializers for Accpick Debtor Management System.

Provides serializers for all models with appropriate field groupings,
validation, and nested representations.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal
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

User = get_user_model()


# ============================================================================
# SIMPLE SERIALIZERS (for nested representations)
# ============================================================================

class UserSimpleSerializer(serializers.ModelSerializer):
    """Simple user serializer for nested representations."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = fields


class DebtorAreaSimpleSerializer(serializers.ModelSerializer):
    """Simple area/salesman serializer for nested representations."""
    
    total_sales = serializers.SerializerMethodField()
    
    class Meta:
        model = DebtorArea
        fields = ['darea', 'dareaname', 'total_sales']
        read_only_fields = fields
    
    def get_total_sales(self, obj):
        return obj.get_total_sales()


class SalesDepartmentSimpleSerializer(serializers.ModelSerializer):
    """Simple department serializer for nested representations."""
    
    class Meta:
        model = SalesDepartment
        fields = ['dept_number', 'dept_name', 'sales_mtd', 'sales_ytd']
        read_only_fields = fields


class DebtorSimpleSerializer(serializers.ModelSerializer):
    """Simple debtor serializer for nested representations."""
    
    class Meta:
        model = Debtor
        fields = ['dno', 'dname', 'dsname', 'dtel', 'email']
        read_only_fields = fields


# ============================================================================
# MAIN SERIALIZERS
# ============================================================================

class DebtorAreaSerializer(serializers.ModelSerializer):
    """
    Serializer for DebtorArea model.
    Handles sales area/salesman with monthly sales tracking.
    """
    
    total_sales = serializers.SerializerMethodField(read_only=True)
    average_monthly_sales = serializers.SerializerMethodField(read_only=True)
    debtor_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = DebtorArea
        fields = [
            'darea',
            'dareaname',
            # Monthly sales (read-only, system-calculated)
            'arsls1', 'arsls2', 'arsls3', 'arsls4', 'arsls5', 'arsls6',
            'arsls7', 'arsls8', 'arsls9', 'arsls10', 'arsls11', 'arsls12',
            # Calculated fields
            'total_sales',
            'average_monthly_sales',
            'debtor_count',
        ]
        read_only_fields = [
            'arsls1', 'arsls2', 'arsls3', 'arsls4', 'arsls5', 'arsls6',
            'arsls7', 'arsls8', 'arsls9', 'arsls10', 'arsls11', 'arsls12',
        ]
    
    def get_total_sales(self, obj):
        return float(obj.get_total_sales())
    
    def get_average_monthly_sales(self, obj):
        return float(obj.get_average_monthly_sales())
    
    def get_debtor_count(self, obj):
        return obj.debtors.count()


class SalesDepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for SalesDepartment model.
    Handles department categorization with sales tracking.
    """
    
    transaction_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = SalesDepartment
        fields = [
            'dept_number',
            'dept_name',
            'sales_mtd',
            'sales_ytd',
            'transaction_count',
        ]
        read_only_fields = ['sales_mtd', 'sales_ytd']
    
    def get_transaction_count(self, obj):
        return obj.transactions.count()


class DebtorSerializer(serializers.ModelSerializer):
    """
    Serializer for Debtor model.
    Separates user-captured fields from system-calculated fields.
    """
    
    # Nested representations
    created_by_detail = UserSimpleSerializer(source='created_by', read_only=True)
    darea_detail = DebtorAreaSimpleSerializer(source='darea', read_only=True)
    
    # Calculated fields
    total_outstanding = serializers.SerializerMethodField(read_only=True)
    overdue_balance = serializers.SerializerMethodField(read_only=True)
    is_over_credit_limit = serializers.SerializerMethodField(read_only=True)
    credit_available = serializers.SerializerMethodField(read_only=True)
    full_address = serializers.SerializerMethodField(read_only=True)
    delivery_address = serializers.SerializerMethodField(read_only=True)
    gross_profit_margin_mtd = serializers.SerializerMethodField(read_only=True)
    gross_profit_margin_ytd = serializers.SerializerMethodField(read_only=True)
    account_status = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Debtor
        fields = [
            # Primary identification (USER-CAPTURED)
            'dno',
            'dname',
            
            # Contact information (USER-CAPTURED)
            'dadd1', 'dadd2', 'dadd3', 'dpcode',
            'delad1', 'delad2', 'delad3', 'delad4',
            'dcontact',
            'dtel', 'tel2', 'dfax', 'email',
            
            # User and area assignment (USER-CAPTURED)
            'created_by',
            'created_by_detail',
            'darea',
            'darea_detail',
            
            # Additional info (USER-CAPTURED)
            'additional_info',
            
            # Credit terms and pricing (USER-CAPTURED)
            'ddiscper',
            'dclimit',
            'price',
            'dintflag',
            'dsname',
            'acctype',
            'vatref',
            'dtaxno',
            'terms',
            'pdisc',
            'discprn',
            'balance_on_pos',
            'blockflag',
            'notes',
            
            # Aging balances (SYSTEM-CALCULATED)
            'dbalbfwd',
            'dcrnt', 'd30', 'd60', 'd90', 'd120', 'd150', 'd180',
            'dposbal',
            
            # Sales and profit (SYSTEM-CALCULATED)
            'dsalesm', 'dsalesy',
            'dprofitm', 'dprofity',
            
            # Last payment (SYSTEM-CALCULATED)
            'damtlpd', 'ddatlpd',
            
            # Metadata
            'dateopened',
            'last_modified',
            
            # Calculated fields
            'total_outstanding',
            'overdue_balance',
            'is_over_credit_limit',
            'credit_available',
            'full_address',
            'delivery_address',
            'gross_profit_margin_mtd',
            'gross_profit_margin_ytd',
            'account_status',
        ]
        read_only_fields = [
            # System-calculated fields
            'dbalbfwd', 'dcrnt', 'd30', 'd60', 'd90', 'd120', 'd150', 'd180', 'dposbal',
            'dsalesm', 'dsalesy', 'dprofitm', 'dprofity',
            'damtlpd', 'ddatlpd',
            'dateopened', 'last_modified',
        ]
    
    def get_total_outstanding(self, obj):
        return float(obj.get_total_outstanding())
    
    def get_overdue_balance(self, obj):
        return float(obj.get_overdue_balance())
    
    def get_is_over_credit_limit(self, obj):
        return obj.is_over_credit_limit()
    
    def get_credit_available(self, obj):
        return float(obj.get_credit_available())
    
    def get_full_address(self, obj):
        return obj.get_full_address()
    
    def get_delivery_address(self, obj):
        return obj.get_delivery_address()
    
    def get_gross_profit_margin_mtd(self, obj):
        return float(obj.get_gross_profit_margin_mtd())
    
    def get_gross_profit_margin_ytd(self, obj):
        return float(obj.get_gross_profit_margin_ytd())
    
    def get_account_status(self, obj):
        """Return human-readable account status."""
        if obj.blockflag:
            return "Blocked"
        elif obj.is_over_credit_limit():
            return "Over Credit Limit"
        elif obj.get_overdue_balance() > 0:
            return "Has Overdue Balance"
        else:
            return "Active"
    
    def validate_terms(self, value):
        """Validate payment terms based on account type."""
        acctype = self.initial_data.get('acctype', '')
        if acctype == Debtor.ACCOUNT_TYPE_CASH and value != '0':
            raise serializers.ValidationError(
                "Cash type customers must have 0 day terms."
            )
        return value
    
    def validate(self, data):
        """Cross-field validation."""
        # Validate that search name is provided or generate it
        if not data.get('dsname') and data.get('dname'):
            data['dsname'] = data['dname'][:5].upper()
        
        return data


class DebtorListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for debtor list views.
    Only includes essential fields for performance.
    """
    
    darea_name = serializers.CharField(source='darea.dareaname', read_only=True)
    is_over_credit_limit = serializers.SerializerMethodField()
    account_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Debtor
        fields = [
            'dno',
            'dname',
            'dsname',
            'dtel',
            'email',
            'darea_name',
            'dposbal',
            'dclimit',
            'blockflag',
            'acctype',
            'is_over_credit_limit',
            'account_status',
        ]
        read_only_fields = fields
    
    def get_is_over_credit_limit(self, obj):
        return obj.is_over_credit_limit()
    
    def get_account_status(self, obj):
        if obj.blockflag:
            return "Blocked"
        elif obj.is_over_credit_limit():
            return "Over Limit"
        else:
            return "Active"


class DebtorTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for DebtorTransaction model.
    Handles all transaction types with nested representations.
    """
    
    debtor_detail = DebtorSimpleSerializer(source='debtor', read_only=True)
    department_detail = SalesDepartmentSimpleSerializer(source='department', read_only=True)
    created_by_detail = UserSimpleSerializer(source='created_by', read_only=True)
    
    # Calculated fields
    net_amount = serializers.SerializerMethodField(read_only=True)
    delivery_address = serializers.SerializerMethodField(read_only=True)
    gross_profit_percentage = serializers.SerializerMethodField(read_only=True)
    transaction_direction = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = DebtorTransaction
        fields = [
            'id',
            'debtor',
            'debtor_detail',
            'dtrano',
            'dtdate',
            'time',
            'dtype',
            'dtsub',
            'dtgst',
            'dttot',
            'dtaxstat',
            'source',
            'ordno',
            'custref',
            'del1', 'del2', 'del3', 'del4',
            'department',
            'department_detail',
            'cost_price',
            'gross_profit',
            'created_by',
            'created_by_detail',
            # Calculated fields
            'net_amount',
            'delivery_address',
            'gross_profit_percentage',
            'transaction_direction',
        ]
        read_only_fields = ['time']
    
    def get_net_amount(self, obj):
        return float(obj.get_net_amount())
    
    def get_delivery_address(self, obj):
        return obj.get_delivery_address()
    
    def get_gross_profit_percentage(self, obj):
        return float(obj.get_gross_profit_percentage())
    
    def get_transaction_direction(self, obj):
        """Return whether transaction is debit or credit."""
        if obj.is_debit_transaction():
            return "Debit"
        elif obj.is_credit_transaction():
            return "Credit"
        return "Unknown"


class DebtorOpenSerializer(serializers.ModelSerializer):
    """
    Serializer for DebtorOpen model.
    Handles open item tracking for Open Item accounting.
    """
    
    debtor_detail = DebtorSimpleSerializer(source='debtor', read_only=True)
    
    # Calculated fields
    amount_paid = serializers.SerializerMethodField(read_only=True)
    payment_percentage = serializers.SerializerMethodField(read_only=True)
    is_fully_paid = serializers.SerializerMethodField(read_only=True)
    is_overdue = serializers.SerializerMethodField(read_only=True)
    days_outstanding = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = DebtorOpen
        fields = [
            'id',
            'debtor',
            'debtor_detail',
            'dtrano',
            'type',
            'date',
            'total',
            'balancedue',
            'ageflag',
            'posted',
            # Calculated fields
            'amount_paid',
            'payment_percentage',
            'is_fully_paid',
            'is_overdue',
            'days_outstanding',
        ]
        read_only_fields = ['balancedue', 'ageflag', 'posted']
    
    def get_amount_paid(self, obj):
        return float(obj.get_amount_paid())
    
    def get_payment_percentage(self, obj):
        return float(obj.get_payment_percentage())
    
    def get_is_fully_paid(self, obj):
        return obj.is_fully_paid()
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()
    
    def get_days_outstanding(self, obj):
        """Calculate days outstanding."""
        from django.utils import timezone
        delta = timezone.now().date() - obj.date
        return delta.days


class DebtorJournalSerializer(serializers.ModelSerializer):
    """
    Serializer for DebtorJournal model.
    Handles debit and credit journal entries.
    """
    
    debtor_detail = DebtorSimpleSerializer(source='debtor', read_only=True)
    created_by_detail = UserSimpleSerializer(source='created_by', read_only=True)
    
    # Calculated fields
    total_aging_allocation = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = DebtorJournal
        fields = [
            'id',
            'debtor',
            'debtor_detail',
            'journal_no',
            'journal_type',
            'date',
            'amount',
            'reference',
            # Aging allocation
            'age_current', 'age_30', 'age_60', 'age_90',
            'age_120', 'age_150', 'age_180',
            'ageflag',
            'posted',
            'batch_no',
            'created_by',
            'created_by_detail',
            'created_at',
            # Calculated fields
            'total_aging_allocation',
        ]
        read_only_fields = ['posted', 'created_at']
    
    def get_total_aging_allocation(self, obj):
        """Calculate total of all aging allocations."""
        total = sum([
            obj.age_current, obj.age_30, obj.age_60, obj.age_90,
            obj.age_120, obj.age_150, obj.age_180
        ])
        return float(total)
    
    def validate(self, data):
        """Validate that aging allocation matches journal amount."""
        debtor = data.get('debtor')
        
        # For Balance Brought Forward accounts
        if debtor and debtor.is_balance_brought_forward():
            total_aging = sum([
                data.get('age_current', 0),
                data.get('age_30', 0),
                data.get('age_60', 0),
                data.get('age_90', 0),
                data.get('age_120', 0),
                data.get('age_150', 0),
                data.get('age_180', 0),
            ])
            
            amount = abs(data.get('amount', 0))
            if abs(total_aging - amount) > Decimal('0.01'):
                raise serializers.ValidationError(
                    "Aging total must balance with journal amount."
                )
        
        return data


class PostDatedChequeSerializer(serializers.ModelSerializer):
    """
    Serializer for PostDatedCheque model.
    Handles PDC management and reminders.
    """
    
    debtor_detail = DebtorSimpleSerializer(source='debtor', read_only=True)
    created_by_detail = UserSimpleSerializer(source='created_by', read_only=True)
    
    # Calculated fields
    is_due_today = serializers.SerializerMethodField(read_only=True)
    is_due_tomorrow = serializers.SerializerMethodField(read_only=True)
    is_overdue = serializers.SerializerMethodField(read_only=True)
    days_until_due = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = PostDatedCheque
        fields = [
            'id',
            'debtor',
            'debtor_detail',
            'cheque_date',
            'amount',
            'cheque_number',
            'bank_name',
            'captured_date',
            'processed',
            'cancelled',
            'notes',
            'created_by',
            'created_by_detail',
            # Calculated fields
            'is_due_today',
            'is_due_tomorrow',
            'is_overdue',
            'days_until_due',
            'status',
        ]
        read_only_fields = ['captured_date', 'processed']
    
    def get_is_due_today(self, obj):
        return obj.is_due_today()
    
    def get_is_due_tomorrow(self, obj):
        return obj.is_due_tomorrow()
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()
    
    def get_days_until_due(self, obj):
        """Calculate days until cheque is due."""
        from django.utils import timezone
        delta = obj.cheque_date - timezone.now().date()
        return delta.days
    
    def get_status(self, obj):
        """Return human-readable status."""
        if obj.cancelled:
            return "Cancelled"
        elif obj.processed:
            return "Processed"
        elif obj.is_due_today():
            return "Due Today"
        elif obj.is_due_tomorrow():
            return "Due Tomorrow"
        elif obj.is_overdue():
            return "Overdue"
        else:
            return "Pending"


class InterestChargeSerializer(serializers.ModelSerializer):
    """
    Serializer for InterestCharge model.
    Handles interest charging on overdue accounts.
    """
    
    debtor_detail = DebtorSimpleSerializer(source='debtor', read_only=True)
    
    class Meta:
        model = InterestCharge
        fields = [
            'id',
            'charge_date',
            'debtor',
            'debtor_detail',
            'start_period',
            'interest_rate',
            'balance_charged',
            'interest_amount',
            'posted',
            'created_at',
        ]
        read_only_fields = ['balance_charged', 'interest_amount', 'posted', 'created_at']


class ReceiptAllocationSerializer(serializers.ModelSerializer):
    """
    Serializer for ReceiptAllocation model.
    Handles allocation of receipts to open items.
    """
    
    receipt_detail = serializers.SerializerMethodField(read_only=True)
    open_item_detail = serializers.SerializerMethodField(read_only=True)
    
    # Calculated fields
    total_applied = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ReceiptAllocation
        fields = [
            'id',
            'receipt_transaction',
            'receipt_detail',
            'open_item',
            'open_item_detail',
            'amount_paid',
            'settlement_discount',
            'fully_paid',
            'allocation_date',
            'created_at',
            # Calculated fields
            'total_applied',
        ]
        read_only_fields = ['created_at']
    
    def get_receipt_detail(self, obj):
        return {
            'dtrano': obj.receipt_transaction.dtrano,
            'date': obj.receipt_transaction.dtdate,
            'total': float(obj.receipt_transaction.dttot),
        }
    
    def get_open_item_detail(self, obj):
        return {
            'dtrano': obj.open_item.dtrano,
            'type': obj.open_item.type,
            'total': float(obj.open_item.total),
            'balance_due': float(obj.open_item.balancedue),
        }
    
    def get_total_applied(self, obj):
        """Total amount applied including discount."""
        return float(obj.amount_paid + obj.settlement_discount)
    
    def validate(self, data):
        """Validate allocation."""
        # Check that debtors match
        receipt = data.get('receipt_transaction')
        open_item = data.get('open_item')
        
        if receipt and open_item:
            if receipt.debtor != open_item.debtor:
                raise serializers.ValidationError(
                    "Receipt and open item must be for the same debtor."
                )
        
        # No settlement discount on part payments
        if not data.get('fully_paid', False) and data.get('settlement_discount', 0) > 0:
            raise serializers.ValidationError(
                "Settlement discount is not allowed on part payments."
            )
        
        return data


# ============================================================================
# SUMMARY/REPORT SERIALIZERS
# ============================================================================

class DebtorAgingSummarySerializer(serializers.Serializer):
    """
    Serializer for age analysis summary.
    Non-model serializer for reporting purposes.
    """
    
    dno = serializers.CharField()
    dname = serializers.CharField()
    dcontact = serializers.CharField()
    dtel = serializers.CharField()
    current = serializers.DecimalField(max_digits=12, decimal_places=2)
    days_30 = serializers.DecimalField(max_digits=12, decimal_places=2)
    days_60 = serializers.DecimalField(max_digits=12, decimal_places=2)
    days_90 = serializers.DecimalField(max_digits=12, decimal_places=2)
    days_120 = serializers.DecimalField(max_digits=12, decimal_places=2)
    days_150 = serializers.DecimalField(max_digits=12, decimal_places=2)
    days_180 = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_outstanding = serializers.DecimalField(max_digits=12, decimal_places=2)
    credit_limit = serializers.DecimalField(max_digits=12, decimal_places=2)


class DebtorPerformanceSerializer(serializers.Serializer):
    """
    Serializer for debtor performance reporting.
    Non-model serializer for reporting purposes.
    """
    
    dno = serializers.CharField()
    dname = serializers.CharField()
    sales_mtd = serializers.DecimalField(max_digits=12, decimal_places=2)
    sales_ytd = serializers.DecimalField(max_digits=12, decimal_places=2)
    profit_mtd = serializers.DecimalField(max_digits=12, decimal_places=2)
    profit_ytd = serializers.DecimalField(max_digits=12, decimal_places=2)
    gp_margin_mtd = serializers.DecimalField(max_digits=5, decimal_places=2)
    gp_margin_ytd = serializers.DecimalField(max_digits=5, decimal_places=2)