from django.db import models

class Supplier(models.Model):
    supno = models.CharField(max_length=10, primary_key=True)
    supname = models.CharField(max_length=50)
    supadd1 = models.CharField(max_length=50, blank=True)
    supadd2 = models.CharField(max_length=50, blank=True)
    supadd3 = models.CharField(max_length=50, blank=True)
    suppadd1 = models.CharField(max_length=50, blank=True)
    suppadd2 = models.CharField(max_length=50, blank=True)
    suppadd3 = models.CharField(max_length=50, blank=True)
    suptel = models.CharField(max_length=20, blank=True)
    supfax = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    supcont = models.CharField(max_length=50, blank=True)
    supouracc = models.CharField(max_length=20, blank=True)
    supterms = models.CharField(max_length=20, blank=True)
    supdisc = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    supbalbfwd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supcrnt = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sup30 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sup60 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sup90 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sup120 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sup150 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sup180 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    suppmt = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    suppmtdate = models.DateField(null=True, blank=True)
    supurchmtd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supurchytd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bank = models.CharField(max_length=50, blank=True)
    bankcode = models.CharField(max_length=10, blank=True)
    bankacc = models.CharField(max_length=20, blank=True)
    updstksp = models.BooleanField(default=False)
    acctype = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.supname

class SupplierTransaction(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    strano = models.CharField(max_length=10)
    stdate = models.DateField()
    sduedate = models.DateField(null=True, blank=True)
    stype = models.CharField(max_length=10)
    stsub = models.CharField(max_length=10)
    stgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sttot = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stref = models.CharField(max_length=20, blank=True)
    grnno = models.CharField(max_length=10, blank=True)
    station = models.CharField(max_length=10, blank=True)
    user = models.CharField(max_length=20, blank=True)

    class Meta:
        unique_together = ('supplier', 'strano')

    def __str__(self):
        return f"{self.supplier.supno} - {self.strano}"

class SupplierOpen(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    trano = models.CharField(max_length=10)
    type = models.CharField(max_length=10)
    date = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balancedue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ageflag = models.CharField(max_length=10)

    class Meta:
        unique_together = ('supplier', 'trano')

    def __str__(self):
        return f"{self.supplier.supno} - {self.trano}"

class ExpenseCategory(models.Model):
    expcat = models.CharField(max_length=10, primary_key=True)
    expcatname = models.CharField(max_length=50)
    expmtd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expinvat = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exp1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exp2 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exp3 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exp4 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exp5 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exp6 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exp7 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exp8 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exp9 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exp10 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exp11 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exp12 = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.expcatname

class ExpenseTransaction(models.Model):
    expcat = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    date = models.DateField()
    trano = models.CharField(max_length=10)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    invat = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    source = models.CharField(max_length=10)
    grnno = models.CharField(max_length=10, blank=True)
    taxind = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.expcat.expcat} - {self.trano}"

class SupplierCreditMaster(models.Model):
    rfcno = models.CharField(max_length=10, primary_key=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    datesent = models.DateField(null=True, blank=True)
    dateretn = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10)

    def __str__(self):
        return self.rfcno

class SupplierCreditTransaction(models.Model):
    rfc = models.ForeignKey(SupplierCreditMaster, on_delete=models.CASCADE)
    type = models.CharField(max_length=10)
    code = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    val = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    qtyrfc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    qtycred = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comment = models.CharField(max_length=100, blank=True)
    purchdate = models.DateField(null=True, blank=True)
    suprefno = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.rfc.rfcno} - {self.code}"

class SupplierPO(models.Model):
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    detail1 = models.CharField(max_length=50, blank=True)
    detail2 = models.CharField(max_length=50, blank=True)
    detail3 = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"PO {self.date} - {self.amount}"
