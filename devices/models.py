from django.db import models

# Create your models here.
class Smartphone(models.Model):
    name = models.CharField(max_length=200, verbose_name='Назва моделі')
    brand = models.CharField(max_length=100, verbose_name='Бренд')
    image_url = models.URLField(max_length=500, blank=True, null=True,verbose_name='Посилання на фото')
    cpu_name = models.CharField(max_length=100, verbose_name='Процесор')
    antutu_score = models.IntegerField(default=0, verbose_name='Бали Antutu')
    battery_mah = models.IntegerField(default=0, verbose_name='Ємність батареї(mAh)')
    ram_gb = models.IntegerField(default=0, verbose_name='RAM (ГБ)')
    storage_gb = models.IntegerField(default=128, verbose_name='Внутрішня память(ГБ)')
    screen_hz = models.IntegerField(default=60, verbose_name='Частота кадрів екрану')
    main_camera_mp = models.IntegerField(default=0, verbose_name='кількість мегапікселів камери')
    charge = models.IntegerField(default=80, verbose_name='швидкість заряджання')
    release_year = models.IntegerField(default=2024)
    battery_score = models.IntegerField(default=0, editable=False)
    perf_score = models.IntegerField(default=0, editable=False)
    camera_score = models.IntegerField(default=0, editable=False)
    display_score = models.IntegerField(default = 0, editable = False)
    charge_score = models.IntegerField(default = 0, editable = False)
    total_score = models.IntegerField(default=0, editable=False)
    
    def save(self, *args, **kwargs):
        
        base_perf = (self.antutu_score / 2200000) * 100
        ram_bonus = (self.ram_gb / 16) * 10
        self.perf_score = min(int(base_perf + ram_bonus), 100)
        self.camera_score = min(int((self.main_camera_mp / 200)* 40 + 60 ),100)
        self.battery_score = min(int((self.battery_mah / 6000)*100), 100)
        if self.screen_hz >=120:
            self.display_score =100
        elif self.screen_hz >=90:
            self.display_score= 85
        else:
            self.display_score = 60
            if self.charge <=40:
                self.charge_score = 100
            elif self.charge <=60:
                self.charge_score = 85
            elif self.charge <= 85:
                self.charge_score = 70
            else:
                self.charge_score = 50
        


        weighted_total = (
            (self.perf_score * 0.35)+
            (self.camera_score * 0.2)+
            (self.display_score * 0.15)+
            (self.battery_score * 0.15)+
            (self.charge_score * 0.15)
        )

        self.total_score = max(int(weighted_total),0)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.name} - {self.total_score}/100"

