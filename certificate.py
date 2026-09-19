"""Arabic PNG result cards drawn entirely with Python/Pillow."""
from io import BytesIO
from pathlib import Path
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

ASSETS=Path(__file__).parent/'assets'
def font(size):
    candidates=[ASSETS/'NotoSansArabic.ttf',Path('C:/Windows/Fonts/tahoma.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]
    for p in candidates:
        if p.exists(): return ImageFont.truetype(str(p),size)
    return ImageFont.load_default(size=size)

def shape(text):
    return get_display(arabic_reshaper.reshape(str(text)))

def write(draw,text,x,y,size=26,color='#153e52',max_width=920,align='right'):
    text=shape(text)
    while size>12 and draw.textbbox((0,0),text,font=font(size))[2]>max_width:
        size-=1
    f=font(size)
    box=draw.textbbox((0,0),text,font=f)
    width=box[2]-box[0]
    left=x-width if align=='right' else x-width/2 if align=='center' else x
    draw.text((left,y-box[1]),text,font=f,fill=color)

def create_result_image(analysis):
    rows=analysis['subject_results']
    footer_y=590+len(rows)*66
    im=Image.new('RGB',(1080,footer_y+170),'#f4f7f6')
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((35,35,1045,im.height-35),radius=26,fill='white',outline='#dce6e2',width=2)
    d.rounded_rectangle((60,60,1020,245),radius=22,fill='#153e52')
    write(d,'درجتي',970,90,53,'white')
    write(d,'خطوتك الجاية تبدأ بفهم درجتك',970,165,25,'#d1e5df')
    logo=ASSETS/'darajati-logo.png'
    if logo.exists():
        icon=Image.open(logo).convert('RGBA'); icon.thumbnail((150,150))
        d.rounded_rectangle((90,80,260,225),radius=18,fill='white')
        im.paste(icon,(100,80),icon)
    write(d,analysis.get('student_name') or 'طالب درجتي',970,280,34,max_width=870)
    system='اللائحة الجديدة 2026' if analysis['system']=='new' else 'الحاسبة التقليدية'
    write(d,f"{analysis['grade']} · {analysis['course']}",970,335,23,max_width=870)
    write(d,system+(' · بيانات تجريبية' if analysis.get('demo') else ''),970,375,20,'#667b84')
    d.rounded_rectangle((90,420,990,550),radius=18,fill='#eaf3ef')
    write(d,f"{analysis['overall_pct']:.2f}%",950,445,48,'#16877c',max_width=390)
    write(d,'النسبة المحوّلة' if analysis['system']=='new' else 'النسبة المحسوبة',950,505,20)
    left_value=f"{analysis['gpa']:.2f} / 4" if analysis['gpa'] is not None else f"{analysis['total_score']:g} / {analysis['total_max']:g}"
    write(d,left_value,430,451,35,max_width=310)
    write(d,'متوسط النقاط الموزون' if analysis['system']=='new' else 'مجموع الدرجات',430,505,20,max_width=310)
    for i,row in enumerate(rows):
        top=580+i*66
        d.rounded_rectangle((85,top,995,top+58),radius=10,fill='#f1f6f4' if i%2==0 else '#ffffff')
        write(d,row['name'],970,top+17,23,max_width=570)
        value=f"{row['percentage']:.1f} / 100" if analysis['system']=='new' else f"{row['score']:g} / {row['max_score']:g}"
        write(d,value,350,top+17,24,color='#a34e4e' if row['below_threshold'] else '#16877c',max_width=240)
    write(d,'بطاقة تخطيطية شخصية · ليست شهادة رسمية',540,footer_y+30,22,align='center')
    write(d,'النتائج تعتمد على مدخلاتك. المرجع النهائي هو سجل الطالب.',540,footer_y+75,18,'#667b84',align='center')
    buffer=BytesIO();im.save(buffer,format='PNG');return buffer.getvalue()
