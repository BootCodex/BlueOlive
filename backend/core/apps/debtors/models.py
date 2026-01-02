from django.db import models

class DebtorArea(models.Model):
    darea = models.CharField(max_length=10, primary_key=True)
    dareaname = models.CharField(max_length=50)
    arsls1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    arsls2 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    arsls3 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    arsls4 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    arsls5 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    arsls6 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    arsls7 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    arsls8 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    arsls9 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    arsls10 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    arsls11 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    arsls12 = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.dareaname

class Debtor(models.Model):
    dno = models.CharField(max_length=10, primary_key=True)
    dname = models.CharField(max_length=50)
    dsname = models.CharField(max_length=30, blank=True)
    dadd1 = models.CharField(max_length=50, blank=True)
    dadd2 = models.CharField(max_length=50, blank=True)
    dadd3 = models.CharField(max_length=50, blank=True)
    dpcode = models.CharField(max_length=10, blank=True)
    dtel = models.CharField(max_length=20, blank=True)
    tel2 = models.CharField(max_length=20, blank=True)
    dfax = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    delad1 = models.CharField(max_length=50, blank=True)
    delad2 = models.CharField(max_length=50, blank=True)
    delad3 = models.CharField(max_length=50, blank=True)
    delad4 = models.CharField(max_length=50, blank=True)
    dcontact = models.CharField(max_length=50, blank=True)
    dtaxno = models.CharField(max_length=20, blank=True)
    darea = models.ForeignKey(DebtorArea, on_delete=models.SET_NULL, null=True, blank=True)
    dbalbfwd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dcrnt = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    d30 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    d60 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    d90 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    d120 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    d150 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    d180 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dsalesm = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dsalesy = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dprofitm = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dprofity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    damtlpd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ddatlpd = models.DateField(null=True, blank=True)
    ddiscper = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    dclimit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dintflag = models.BooleanField(default=False)
    price = models.CharField(max_length=10, blank=True)
    acctype = models.CharField(max_length=10, blank=True)
    terms = models.CharField(max_length=20, blank=True)
    pdisc = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discprn = models.BooleanField(default=False)
    dposbal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    blockflag = models.BooleanField(default=False)
    dateopened = models.DateField(null=True, blank=True)
    vatref = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.dname

class DebtorTransaction(models.Model):
    debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE)
    dtrano = models.CharField(max_length=10)
    dtdate = models.DateField()
    time = models.TimeField()
    dtype = models.CharField(max_length=10)
    dtsub = models.CharField(max_length=10)
    dtgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dttot = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dtaxstat = models.CharField(max_length=10)
    source = models.CharField(max_length=10)
    ordno = models.CharField(max_length=10, blank=True)
    custref = models.CharField(max_length=20, blank=True)
    del1 = models.CharField(max_length=50, blank=True)
    del2 = models.CharField(max_length=50, blank=True)
    del3 = models.CharField(max_length=50, blank=True)
    del4 = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = ('debtor', 'dtrano')

    def __str__(self):
        return f"{self.debtor.dno} - {self.dtrano}"

class DebtorOpen(models.Model):
    debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE)
    dtrano = models.CharField(max_length=10)
    type = models.CharField(max_length=10)
    date = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balancedue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ageflag = models.CharField(max_length=10)
    posted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('debtor', 'dtrano')

    def __str__(self):
        return f"{self.debtor.dno} - {self.dtrano}"
