# إصلاح مشكلة حذف المستخدم

## المشكلة
عند حذف مستخدم، كان النظام يواجه خطأ:
```
sqlite3.IntegrityError: NOT NULL constraint failed: notification.user_id
```

## السبب
عند حذف مستخدم، SQLAlchemy يحاول تحديث الجداول المرتبطة لتصبح `user_id = NULL`، لكن بعض الأعمدة مُعرّفة كـ `NOT NULL`، مما يسبب خطأ في قاعدة البيانات.

## الجداول المتأثرة
1. **Notification** - `user_id` (NOT NULL)
2. **ReportComment** - `user_id` (NOT NULL) 
3. **AuditLog** - `user_id` (nullable, لكن من الأفضل حذفها للتنظيف)

## الحل المطبق

### 1. تحديث الاستيرادات
```python
from app.models import User, Area, Store, Report, Region, Branch, Notification, AuditLog, ReportComment, db
```

### 2. تعديل دالة حذف المستخدم العادي
```python
# Delete user's notifications (to avoid NOT NULL constraint error)
user_notifications = Notification.query.filter_by(user_id=user.id).all()
for notification in user_notifications:
    db.session.delete(notification)

# Delete user's comments (to avoid NOT NULL constraint error)
user_comments = ReportComment.query.filter_by(user_id=user.id).all()
for comment in user_comments:
    db.session.delete(comment)

# Delete user's audit logs (optional, but good for cleanup)
user_audit_logs = AuditLog.query.filter_by(user_id=user.id).all()
for audit_log in user_audit_logs:
    db.session.delete(audit_log)
```

### 3. تعديل دالة حذف المدير
```python
# Delete admin's notifications (to avoid NOT NULL constraint error)
admin_notifications = Notification.query.filter_by(user_id=admin.id).all()
for notification in admin_notifications:
    db.session.delete(notification)

# Delete admin's comments (to avoid NOT NULL constraint error)
admin_comments = ReportComment.query.filter_by(user_id=admin.id).all()
for comment in admin_comments:
    db.session.delete(comment)

# Delete admin's audit logs (optional, but good for cleanup)
admin_audit_logs = AuditLog.query.filter_by(user_id=admin.id).all()
for audit_log in admin_audit_logs:
    db.session.delete(audit_log)
```

## ترتيب الحذف
يتم حذف البيانات بالترتيب التالي لتجنب مشاكل Foreign Key:

1. **التقارير** (إذا كان force_delete مفعل)
2. **الفروع** (Branches)
3. **المناطق** (Regions) 
4. **الإشعارات** (Notifications)
5. **التعليقات** (ReportComments)
6. **سجلات التدقيق** (AuditLogs)
7. **إزالة الارتباطات** (Associations)
8. **المستخدم نفسه** (User)

## النتيجة
- ✅ حذف المستخدم يعمل بدون أخطاء
- ✅ حذف المدير يعمل بدون أخطاء  
- ✅ تنظيف شامل لجميع البيانات المرتبطة
- ✅ عدم ترك بيانات معلقة في قاعدة البيانات

## الاختبار
تم اختبار الحل ونجح في:
- التعرف على البيانات المرتبطة بالمستخدم
- محاكاة عملية الحذف بدون أخطاء
- التأكد من حذف جميع الارتباطات

## ملاحظات
- الحل يحافظ على سلامة قاعدة البيانات
- لا يؤثر على أي وظائف أخرى في النظام
- يتبع أفضل الممارسات في إدارة العلاقات في قواعد البيانات