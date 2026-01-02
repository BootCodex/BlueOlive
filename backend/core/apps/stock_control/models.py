from django.db import models

class Department(models.Model):
    dept = models.CharField(max_length=10, primary_key=True)
    deptname = models.CharField(max_length=50)
    slsmtd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sls1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sls2 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sls3 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sls4 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sls5 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sls6 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sls7 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sls8 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sls9 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sls10 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sls11 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sls12 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    serialtrac = models.BooleanField(default=False)
    chargscrap = models.BooleanField(default=False)

    def __str__(self):
        return self.deptname

class StockItem(models.Model):
    code = models.CharField(max_length=20, primary_key=True)
    descrip = models.CharField(max_length=50)
    supno = models.CharField(max_length=10, blank=True)
    dept = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    taxind = models.CharField(max_length=10)
    cprice = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    avecost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sprice = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sprice1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sprice2 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mup = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    mup1 = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    mup2 = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    reord = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    qoh = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    qsoldm = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    qsoldy = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vsoldm = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vsoldy = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gpm = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gpy = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    qtybystock = models.BooleanField(default=False)
    scountflag = models.BooleanField(default=False)
    clostock = models.BooleanField(default=False)
    datelsold = models.DateField(null=True, blank=True)
    datelpurch = models.DateField(null=True, blank=True)
    lastsup = models.CharField(max_length=10, blank=True)
    specstdate = models.DateField(null=True, blank=True)
    specendate = models.DateField(null=True, blank=True)
    spprice1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    spprice2 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    spprice3 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bfwdqty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bfwdval = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    qtysord = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    qtyord = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    qtypurchm = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    qtypurchy = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    newpr = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    newpr1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    newpr2 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    newprdate = models.DateField(null=True, blank=True)
    sellqty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supcode = models.CharField(max_length=10, blank=True)
    maxdisc = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    allownegsl = models.BooleanField(default=False)
    bin = models.CharField(max_length=20, blank=True)
    jcbfwdval = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lbbfwdval = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rfbfwdval = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pack = models.CharField(max_length=10, blank=True)
    kvi = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.descrip

class StockTransaction(models.Model):
    trano = models.CharField(max_length=10)
    code = models.ForeignKey(StockItem, on_delete=models.CASCADE)
    qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    val = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(max_length=10)
    date = models.DateField()
    time = models.TimeField()
    dept = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxind = models.CharField(max_length=10)
    source = models.CharField(max_length=10)
    dno = models.CharField(max_length=10, blank=True)
    supno = models.CharField(max_length=10, blank=True)
    comments = models.CharField(max_length=100, blank=True)
    stdprice = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.trano} - {self.code.code}"

class BOM(models.Model):
    mastcode = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name='bom_master')
    icode = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name='bom_item')
    iqty = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.mastcode.code} -> {self.icode.code}"

class Shrink(models.Model):
    scode = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name='shrink_master')
    bcode = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name='shrink_bulk')
    sinbulk = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.scode.code} -> {self.bcode.code}"

class SerialNumber(models.Model):
    serialno = models.CharField(max_length=50, primary_key=True)
    itemdetail = models.CharField(max_length=100)
    date = models.DateField()
    transtype = models.CharField(max_length=10)
    transno = models.CharField(max_length=10)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    warranper = models.IntegerField(default=0)
    code = models.ForeignKey(StockItem, on_delete=models.CASCADE)
    comment1 = models.CharField(max_length=100, blank=True)
    comment2 = models.CharField(max_length=100, blank=True)
    comment3 = models.CharField(max_length=100, blank=True)
    comment4 = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=50, blank=True)
    add1 = models.CharField(max_length=50, blank=True)
    add2 = models.CharField(max_length=50, blank=True)
    add3 = models.CharField(max_length=50, blank=True)
    tel = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    stolen = models.BooleanField(default=False)

    def __str__(self):
        return self.serialno
