from django.db import models

class PurchaseOrder(models.Model):
    quoteno = models.CharField(max_length=10, primary_key=True)
    date = models.DateField()
    expdate = models.DateField(null=True, blank=True)
    name = models.CharField(max_length=50)
    add1 = models.CharField(max_length=50, blank=True)
    add2 = models.CharField(max_length=50, blank=True)
    add3 = models.CharField(max_length=50, blank=True)
    tel = models.CharField(max_length=20, blank=True)
    comment1 = models.CharField(max_length=100, blank=True)
    comment2 = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salesman = models.CharField(max_length=20, blank=True)
    stanum = models.CharField(max_length=10, blank=True)
    dno = models.CharField(max_length=10, blank=True)
    email = models.EmailField(blank=True)
    datemailed = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.quoteno

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    code = models.CharField(max_length=20)
    qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sprice = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    disc = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    comments = models.CharField(max_length=100, blank=True)
    dept = models.CharField(max_length=10, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxind = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.purchase_order.quoteno} - {self.code}"

class PurchaseUpdate(models.Model):
    supname = models.CharField(max_length=50)
    department = models.CharField(max_length=10)
    stockcode = models.CharField(max_length=20)
    descrip = models.CharField(max_length=50)
    unitofmeas = models.CharField(max_length=10, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sell1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sell2 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sell3 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    effectdate = models.DateField()

    def __str__(self):
        return f"{self.supname} - {self.stockcode}"
