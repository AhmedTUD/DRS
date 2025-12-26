#!/bin/bash

echo "🔧 إضافة دعم PWA محسن للقوالب..."

# إضافة سكريبت PWA إلى base.html
docker-compose -f docker-compose.simple.yml exec web python -c "
import os
import re

# قراءة ملف base.html
base_template_path = '/app/app/templates/base.html'
if os.path.exists(base_template_path):
    with open(base_template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # التحقق من وجود سكريبت PWA
    if 'fix_pwa_http.js' not in content:
        # إضافة سكريبت PWA قبل إغلاق body
        pwa_script = '''
    <!-- PWA Support -->
    <script src=\"{{ url_for('static', filename='js/fix_pwa_http.js') }}\"></script>
</body>'''
        
        # استبدال </body> بالسكريبت الجديد
        content = content.replace('</body>', pwa_script)
        
        # كتابة الملف المحدث
        with open(base_template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print('✅ تم إضافة دعم PWA إلى base.html')
    else:
        print('✅ دعم PWA موجود بالفعل في base.html')
else:
    print('❌ ملف base.html غير موجود')
"

echo "✅ تم تحديث دعم PWA!"
echo ""
echo "🌐 الآن PWA سيعمل بشكل أفضل مع:"
echo "- تحقق تلقائي من دعم PWA"
echo "- رسائل توضيحية للمستخدم"
echo "- تعليمات تثبيت يدوية"
echo "- دعم أفضل لـ HTTP"