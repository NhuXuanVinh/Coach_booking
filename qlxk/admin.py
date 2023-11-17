from django.contrib import admin
from .models import Users,  Xe, Chuyenxe, Nhanvienxe, Ve, Datve, Danhgia, Ghe, Dieukhien

class ChuyenxeAmin(admin.ModelAdmin):
    list_display=("chuyenxe_id","origin", "destination", "chuyenxe_date")
    
class NhanvienAdmin(admin.ModelAdmin):
    list_display=["nhanvien_id", "nhanvien_name"]
    
class XeAdmin(admin.ModelAdmin):
    list_display=["bien_so", "xe_name"]


# Register your models here.
admin.site.register(Users)
admin.site.register(Xe, XeAdmin)
admin.site.register(Chuyenxe, ChuyenxeAmin)
admin.site.register(Nhanvienxe, NhanvienAdmin)
admin.site.register(Ve)
admin.site.register(Datve)
admin.site.register(Danhgia)
admin.site.register(Ghe)
admin.site.register(Dieukhien)

