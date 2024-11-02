from flask import Flask, render_template, request, redirect, url_for, send_file
import uuid
import os
import qrcode

app = Flask(__name__)

# بيانات افتراضية للاختبار
data = {
    "رقم التصريحة": "8003413391330",
    "دائرة الاصدار": "كمارك اقليم كوردستان - إبراهيم الخليل",
    "تاریخ/وقت التنظيم": "2024-07-23 09:38:35",
    "رقم السيارة/الرحلة": "27RV419/27AAZ639",
    "اسم السائق": "YAVUZ UGUR",
    "اسم التاجر/الجهة المستوردة": "كومبانيا كيسته",
    "اسم الوكيل الاخراجي": "سفر مجيد محمد",
    "رقم منافيست النقل البري": "8672401126249",
    "رقم استمارة الجباية": "2598074",
    "مكان التسليم/التفريغ": "دهوك",
    "مجموع الرسم الکمركي": "995 دولار",
    "مجموع الضريبة": "448 دولار",
    "قيمة البضاعة": "19900.00 دولار",
    "table_data": [
        {
            "رمز HS": "39210000",
            "نوع البضاعة": "الواح وصفائح ولفات واشرطة من منتجات خلوية",
            "الكمية": "1",
            "التعبئة": "19900",
            "م. الكمية": "19900",
            "الوحدة": "کغم",
            "الرسم": "995",
            "الضريبة": "448"
        }
    ]
}

# مسار حفظ الملفات
SAVE_DIR = "saved_forms"
os.makedirs(SAVE_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html', data=data)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    global data
    if request.method == 'POST':
        # تحديث الحقول الأساسية
        for key in data.keys():
            if key != 'table_data':
                data[key] = request.form.get(key)
        
        # تحديث جدول table_data
        data['table_data'] = []
        index = 0
        while f"table_data_{index}_رمز HS" in request.form:
            item = {
                "رمز HS": request.form.get(f"table_data_{index}_رمز HS"),
                "نوع البضاعة": request.form.get(f"table_data_{index}_نوع البضاعة"),
                "الكمية": request.form.get(f"table_data_{index}_الكمية"),
                "التعبئة": request.form.get(f"table_data_{index}_التعبئة"),
                "م. الكمية": request.form.get(f"table_data_{index}_م. الكمية"),
                "الوحدة": request.form.get(f"table_data_{index}_الوحدة"),
                "الرسم": request.form.get(f"table_data_{index}_الرسم"),
                "الضريبة": request.form.get(f"table_data_{index}_الضريبة")
            }
            data['table_data'].append(item)
            index += 1
        
        # حفظ البيانات كنموذج HTML مستقل
        unique_id = str(uuid.uuid4())
        filename = f"{SAVE_DIR}/{unique_id}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(render_template('index.html', data=data))

        # توليد رمز QR للرابط
        file_url = url_for('view_saved_form', unique_id=unique_id, _external=True)
        qr = qrcode.make(file_url)
        qr_filename = f"{SAVE_DIR}/{unique_id}_qr.png"
        qr.save(qr_filename)

        # عرض الرابط العشوائي للملف المحفوظ
        return redirect(url_for('view_saved_form', unique_id=unique_id))
    
    return render_template('form.html', data=data)

# دالة عرض النموذج المحفوظ
@app.route('/saved/<unique_id>')
def view_saved_form(unique_id):
    filename = f"{SAVE_DIR}/{unique_id}.html"
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # رابط لصفحة الباركود
        qr_url = url_for('view_qr', unique_id=unique_id)
        
        return render_template('saved_view.html', content=content, qr_url=qr_url)
    else:
        return "الملف غير موجود", 404

# دالة لعرض صفحة الباركود فقط
@app.route('/saved/<unique_id>/qr')
def view_qr(unique_id):
    qr_filename = f"{SAVE_DIR}/{unique_id}_qr.png"
    if os.path.exists(qr_filename):
        return render_template('qr_view.html', qr_filename=qr_filename)
    else:
        return "الباركود غير موجود", 404

# دالة لإرسال صورة QR
@app.route('/qr_image/<unique_id>')
def get_qr(unique_id):
    qr_filename = f"{SAVE_DIR}/{unique_id}_qr.png"
    if os.path.exists(qr_filename):
        return send_file(qr_filename, mimetype='image/png')
    else:
        return "الباركود غير موجود", 404

if __name__ == '__main__':
    app.run(debug=True)
