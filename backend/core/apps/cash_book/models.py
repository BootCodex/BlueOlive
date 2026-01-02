from django.db import models

class CashBookTransaction(models.Model):
    cbtrano = models.CharField(max_length=10, primary_key=True)
    cbref = models.CharField(max_length=20)
    cbaudit = models.CharField(max_length=10)
    date = models.DateField()
    type = models.CharField(max_length=10)
    catno = models.CharField(max_length=10)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cbtag = models.CharField(max_length=10)
    taxind = models.CharField(max_length=10)

    def __str__(self):
        return self.cbtrano

class CashBookCheque(models.Model):
    cbtrano = models.CharField(max_length=10, primary_key=True)
    cbref = models.CharField(max_length=20)
    date = models.DateField()
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cbtag = models.CharField(max_length=10)
    type = models.CharField(max_length=10)

    def __str__(self):
        return self.cbtrano

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

class IncomeCategory(models.Model):
    inccat = models.CharField(max_length=10, primary_key=True)
    inccatname = models.CharField(max_length=50)
    incmtd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    incinvat = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    inc1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    inc2 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    inc3 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    inc4 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    inc5 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    inc6 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    inc7 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    inc8 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    inc9 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    inc10 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    inc11 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    inc12 = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.inccatname

class CashierShift(models.Model):
    date = models.DateField()
    time = models.TimeField()
    invcount = models.IntegerField(default=0)
    invtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cncount = models.IntegerField(default=0)
    cntotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cslcount = models.IntegerField(default=0)
    csltotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cretcount = models.IntegerField(default=0)
    crettotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    arrecount = models.IntegerField(default=0)
    arrectotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    poutcount = models.IntegerField(default=0)
    pouttotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    newlbcount = models.IntegerField(default=0)
    newlbtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lbreccount = models.IntegerField(default=0)
    lbrectotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lbcanccount = models.IntegerField(default=0)
    lbcantotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tend1total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tend1count = models.IntegerField(default=0)
    tend2total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tend2count = models.IntegerField(default=0)
    tend3total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tend3count = models.IntegerField(default=0)
    tend4total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tend4count = models.IntegerField(default=0)
    abancount = models.IntegerField(default=0)
    abantotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    adjust = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    adjcount = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.date} {self.time}"
