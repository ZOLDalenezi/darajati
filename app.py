"""Darajati: a Python/Streamlit student grade planning application."""
import os
import time
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from calculations import GRADES, GPA_SCALE, SOURCE_URL, analyze, subjects_for, practical, cumulative, target_gap, next_steps
from brand import apply_theme, header, heading
from certificate import create_result_image
from mishal import reply, local_reply

ROOT=Path(__file__).parent
load_dotenv(ROOT/'secrets.env',override=False)
st.set_page_config(page_title='درجتي | افهم درجتك وخطط لهدفك',page_icon=str(ROOT/'assets/darajati-logo.png'),layout='wide',initial_sidebar_state='collapsed')
apply_theme();header()
ss=st.session_state
for key,value in dict(page='الرئيسية',analysis=None,messages=[]).items():
    if key not in ss: ss[key]=value

FORM_KEYS={'system','grade','course','entry_mode','uniform','uniform_amount','exempt','card_name'}

def save_form():
    ss.form_state={k:v for k,v in ss.items() if k in FORM_KEYS or k.startswith('input_')}

def go(page):
    if ss.page=='الحاسبة':save_form()
    ss.page=page

def load_demo():
    grade='الصف الحادي عشر - علمي'
    marks={n:float([95,98,97,94,96,90,78,84,87,82,91,94,76][i]) for i,(n,w) in enumerate(subjects_for(grade,'new'))}
    ss.analysis=analyze(grade,marks,'new',name='زائر المعرض',demo=True)
    ss.form_state={'system':'اللائحة الجديدة 2026','grade':grade,'course':'الكورس الأول','entry_mode':'درجاتي الفعلية','card_name':'زائر المعرض'}
    ss.form_state.update({f'input_new_{grade}_الكورس الأول_درجاتي الفعلية_{i}':v for i,v in enumerate(marks.values())})
    ss.messages=[];ss.page='نتيجتي'

def new_visitor():
    for k in list(ss):
        if k!='page': del ss[k]
    ss.page='الرئيسية'

with st.container(key='navigation'):
    pages=['الرئيسية','الحاسبة','نتيجتي','مشعل','الدليل','عن درجتي']
    for col,page in zip(st.columns(len(pages)),pages):
        col.button(page,key='nav_'+page,type='primary' if ss.page==page else 'secondary',on_click=go,args=(page,),width='stretch')

def render_home():
    st.markdown('''<div class="hero"><div><span class="eyebrow">من طالب… لكل طالب في الكويت</span><h1>درجتك أوضح.<br><em>وخطوتك أذكى.</em></h1><p>احسب نتيجتك، افهم نظام الدرجات الجديد، واكتشف مع مشعل وين تركز عشان تقرّب من هدفك.</p></div><div class="hero-preview"><span class="preview-label">صورة أوضح عن مستواك · مثال توضيحي</span><div class="preview-number">87.40 <small>%</small></div><div class="progress-track"><div class="progress-fill"></div></div><div class="preview-note">كل درجة تفهمها… خطوة تعرف تخطط لها.</div></div></div>''',unsafe_allow_html=True)
    a,b=st.columns(2)
    a.button('ابدأ حساب درجتك',type='primary',width='stretch',on_click=go,args=('الحاسبة',))
    b.button('جرّب بمثال جاهز',width='stretch',on_click=load_demo)
    st.write('')
    for col,num,title,copy in zip(st.columns(3),['01','02','03'],['اختَر نظامك','افهم نتيجتك','خطط مع مشعل'],['الحاسبة التقليدية واللائحة الجديدة 2026، كل وحدة في مكانها.','تفاصيل المواد، فرص التحسين، وبطاقة نتيجة تقدر تحفظها.','أسئلة بسيطة وتحليل واضح يساعدك تحدد خطوتك القادمة.']):
        col.markdown(f'<div class="feature"><span class="num">{num}</span><h3>{title}</h3><p>{copy}</p></div>',unsafe_allow_html=True)
    st.markdown('<div class="mishal-callout"><h3>هلا، أنا مشعل.</h3><p>مو بس أعطيك رقم. أساعدك تفهمه: وين نقاط قوتك؟ وأي مادة تستحق وقتك أكثر؟</p></div>',unsafe_allow_html=True)
    st.button('افتح المحادثة مع مشعل ←',on_click=go,args=('مشعل',),width='stretch')

def render_calculator():
    for k,v in ss.get('form_state',{}).items():
        if k not in ss:ss[k]=v
    heading('خلّنا نحسبها صح.','اختَر النظام المطابق لدراستك. النتائج هنا للتخطيط والمقارنة.')
    chosen=st.radio('نظام الحساب',['اللائحة الجديدة 2026','الحاسبة التقليدية (القديمة)'],horizontal=True,key='system')
    system='new' if chosen.startswith('اللائحة') else 'legacy'
    st.caption('للثانوية في اللائحة الشاملة 2026. أدخل كل مادة من 100. نظام المسارات التجريبي مستقل؛ تفاصيله في الدليل.' if system=='new' else 'الحسبة التقليدية: مجموع درجاتك ÷ مجموع الدرجات العظمى. استخدمها للمقارنة أو للنتائج السابقة.')
    a,b=st.columns(2)
    grade=a.selectbox('الصف والمسار',list(GRADES),key='grade')
    course=b.selectbox('الفترة',['الكورس الأول','الكورس الثاني','العام كامل (الكورسان)'],key='course')
    annual=course.startswith('العام')
    mode=st.radio('طريقة الإدخال',['درجاتي الفعلية','تجربة الخصم'],horizontal=True,key='entry_mode')
    quick=mode=='تجربة الخصم'
    uniform=False;deduction=0;exempt=True
    if quick:
        st.caption('هذه محاكاة تبدأ من الدرجة الكاملة. الخصم الفارغ يعني صفر خصم، وليس درجة فعلية.')
        uniform=st.toggle('طبّق خصمًا موحدًا على المواد',value=True,key='uniform')
        if uniform:
            deduction=st.number_input('عدد الدرجات المخصومة',0.0,100.0,5.0,step=1.0,key='uniform_amount')
            exempt=st.checkbox('اترك المواد العملية والاختيار الحر كاملة',value=True,key='exempt')
        if annual: st.caption('في تجربة الخصم السنوية، يُطبّق السيناريو نفسه على الكورسين.')
    if system=='new':
        with st.expander('شلون أجمع درجة المادة من 100؟'):
            st.write('المادة النظرية: أعمال المتعلم 25 + الاختبار القصير 15 + النهائي 60. أعمال المتعلم: مشاركة 6، واجبات 6، سلوك 6، مشروع 7.')
            st.write('المواد العملية: الاختبارات والمشاريع 60 + السلوك والتعامل مع الأدوات 20 + المشاركة والتفاعل 20.')
            c1,c2,c3=st.columns(3)
            work=c1.number_input('أعمال المتعلم / 25',0.0,25.0,20.0,key='component_work')
            quiz=c2.number_input('القصير / 15',0.0,15.0,12.0,key='component_quiz')
            exam=c3.number_input('النهائي / 60',0.0,60.0,50.0,key='component_exam')
            st.info(f'المجموع = {work+quiz+exam:g} / 100. انقله إلى خانة المادة المناسبة أدناه.')
    values={};second={};missing=[]
    for i,(name,weight) in enumerate(subjects_for(grade,system)):
        maximum=100 if system=='new' else weight
        prefix=f'input_{system}_{grade}_{course}_{mode}_{i}'
        with st.container(border=True):
            cols=st.columns([2,1,1] if annual and not quick else [2,1])
            a,b=cols[:2]
            a.markdown(f'**{name}**')
            a.caption(f'وزن المادة: {weight} · الدرجة من {maximum}'+(' · مادة عملية' if practical(name) else ''))
            if uniform and quick:
                value=float(maximum if exempt and practical(name) else max(0,maximum-deduction))
                b.metric('بعد الخصم',f'{value:g} / {maximum}')
            elif quick:
                entered=b.number_input(f'خصم {name}',min_value=0.0,max_value=float(maximum),value=None,step=1.0,key=prefix,placeholder='صفر خصم')
                value=maximum-(entered or 0)
            else:
                value=b.number_input(f'{name}'+(' · الأول' if annual else ''),min_value=0.0,max_value=float(maximum),value=None,step=1.0,key=prefix,placeholder=f'من {maximum}')
            values[name]=value
            if value is None: missing.append(name)
            if annual:
                value2=value if quick else cols[2].number_input(f'{name} · الثاني',min_value=0.0,max_value=float(maximum),value=None,step=1.0,key=prefix+'_second',placeholder=f'من {maximum}')
                second[name]=value2
                if value2 is None: missing.append(name+' (الثاني)')
    name=st.text_input('الاسم الظاهر على البطاقة (اختياري)',max_chars=50,key='card_name',placeholder='اسمك الأول أو لقبك')
    if quick:
        preview=analyze(grade,values,system,course,second if annual else None,name)
        st.info(f"النسبة المتوقعة: {preview['overall_pct']:.2f}%"+(' · بعد التحويل بالنقاط' if system=='new' else ''))
    if missing: st.caption(f'باقي {len(missing)} خانة. أدخل صفرًا فقط إذا كانت درجتك فعلًا صفرًا.')
    if st.button('اعرض نتيجتي ←',type='primary',width='stretch'):
        if missing: st.warning('أكمل الدرجات قبل الحساب: '+'، '.join(missing[:4]))
        else:
            save_form()
            ss.analysis=analyze(grade,values,system,course,second if annual else None,name)
            ss.analysis['simulation']=quick
            ss.messages=[];ss.page='نتيجتي';st.rerun()

@st.cache_data(show_spinner=False,ttl=600,max_entries=32)
def result_card(analysis):return create_result_image(analysis)

def render_result():
    analysis=ss.analysis
    heading('هذه نتيجتك. وهذه فرصتك.','اقرأ التفاصيل، جرّب هدفك، وخذ نسختك معك.')
    if not analysis:
        st.info('ما عندك نتيجة حتى الآن. احسب درجاتك أو جرّب المثال الجاهز.')
        st.button('جرّب مثال المعرض',on_click=load_demo,type='primary');return
    if analysis.get('demo'): st.info('هذه بيانات تجريبية لزائر المعرض، وليست درجاتك الشخصية.')
    if analysis.get('simulation'): st.info('نتيجة محاكاة خصم؛ ليست درجات فعلية.')
    st.caption(analysis['grade']+' · '+analysis['course']+' · '+('اللائحة الجديدة 2026' if analysis['system']=='new' else 'الحاسبة التقليدية'))
    stat_values=[(f"{analysis['overall_pct']:.2f}%",'النسبة المحوّلة' if analysis['system']=='new' else 'النسبة المحسوبة'),(f"{analysis['gpa']:.2f} / 4" if analysis['gpa'] is not None else f"{analysis['total_score']:g}",'متوسط النقاط الموزون' if analysis['system']=='new' else 'مجموع الدرجات'),(str(len(analysis['subject_results'])),'مادة في حسابك')]
    for col,(value,label) in zip(st.columns(3),stat_values):
        col.markdown(f'<div class="stat"><b>{value}</b><span>{label}</span></div>',unsafe_allow_html=True)
    if analysis['failing']:
        st.warning('درجات أقل من 50% تحتاج انتباه: '+'، '.join(analysis['failing'])+'. هذه قراءة للدرجات، وليست حكم نجاح رسمي.')
    if analysis['system']=='new':
        st.caption('النسبة أعلاه محوّلة من النقاط، وليست متوسط الدرجات الخام. تطبق المعادلة المنشورة حتى لشريحة F؛ ظهور نسبة محوّلة لا يعني اجتياز المادة. الكسر لا يُقرّب إلى شريحة أعلى.')
    left,right=st.columns([1.15,1])
    with left:
        st.subheader('وين تقدر تتحسن؟')
        steps=next_steps(analysis)
        if steps:
            for step in steps[:3]:
                st.markdown(f"**{step['name']}** — +{step['need']:g} درجة، ترفع نسبتك بنحو **{step['gain']:.2f}** نقطة مئوية"+(f" · إلى {step['goal']}" if analysis['system']=='new' else ''))
        else: st.write('راجع تفاصيل المواد مع مشعل لوضع خطة تناسبك.')
        st.button('ناقش نتيجتك مع مشعل',type='primary',on_click=go,args=('مشعل',),width='stretch')
    with right:
        with st.container(border=True):
            st.subheader('هدفي القادم')
            target=st.slider('النسبة التي أطمح لها',50,100,90,key='target')
            gap=target_gap(analysis,target)
            if gap==0: st.success('وصلت إلى هذا الهدف في حسابك الحالي!')
            elif analysis['system']=='legacy': st.write(f'تحتاج **{gap:.2f}** درجة إضافية موزعة على المواد للوصول إلى **{target}%**.')
            else: st.write(f"الفارق عن هدفك **{max(0,target-analysis['overall_pct']):.2f} نقطة مئوية**. التحسن بالنظام الجديد يعتمد على الانتقال بين شرائح المواد؛ راجع الفرص المقترحة.")
    with st.expander('تفاصيل جميع المواد'):
        table=[]
        for r in analysis['subject_results']:
            row={'المادة':r['name'],'الدرجة الخام / 100':round(r['percentage'],2)} if analysis['system']=='new' else {'المادة':r['name'],'درجتك':round(r['score'],2),'العظمى':r['max_score']}
            if analysis['system']=='new': row.update({'النقاط':round(r['gpa'],3),'الوزن':r['max_score']})
            table.append(row)
        st.table(table)
    st.subheader('بطاقتك جاهزة')
    st.caption('معاينة مباشرة. الحفظ اختياري، ولا نطلب اسمًا كاملًا.')
    card=result_card(analysis)
    c1,c2=st.columns(2)
    c1.image(card,width='stretch')
    with c2:
        st.markdown('### خذ نتيجتك معك')
        st.write('احفظ الصورة في جهازك، أو اكتفِ بمشاهدتها هنا. البطاقة شخصية وتقديرية وليست شهادة صادرة من الوزارة.')
        st.download_button('حفظ بطاقة النتيجة',card,'darajati-result.png','image/png',type='primary',width='stretch')
        st.button('ارجع وعدّل درجاتك',on_click=go,args=('الحاسبة',),width='stretch')

def get_secret(key,default=''):
    value=os.getenv(key)
    if value:return value
    try:return st.secrets.get(key,default)
    except Exception:return default

def render_chat():
    heading('مشعل، معك خطوة بخطوة.','اسأل عن درجتك، خطتك، أو النظام الجديد.')
    analysis=ss.analysis
    if analysis:st.caption(f"{'مثال تجريبي' if analysis.get('demo') else 'آخر نتيجة'} · {analysis['grade']} · {analysis['overall_pct']:.2f}%")
    else:st.info('تقدر تسأل أسئلة عامة. للتحليل الشخصي، احسب نتيجتك أولًا.')
    api_key=get_secret('GEMINI_API_KEY')
    online=st.toggle('تفعيل المحادثة الذكية عبر الإنترنت',value=bool(api_key),key='online',help='عند تفعيلها تُرسل رسائلك وتفاصيل الدرجات إلى Google Gemini. اسم البطاقة لا يُرسل.')
    st.caption('الأسئلة السريعة تعمل فورًا من درجاتك. المحادثة الذكية ترسل السؤال والدرجات إلى Gemini دون اسم البطاقة؛ تجنب البيانات الشخصية.')
    prompt=None;quick=False
    for row in [['وين أركز؟','شنو أقوى موادي؟'],['اقترح خطة مذاكرة','اشرح النظام الجديد']]:
        for col,q in zip(st.columns(2),row):
            if col.button(q,width='stretch'):prompt=q;quick=True
    if not ss.messages:
        with st.chat_message('assistant',avatar='🎓'):st.write('هلا فيك! خلّنا نحول الأرقام إلى خطوة واضحة. اختَر سؤالًا فوق أو اكتب اللي في بالك.')
    for msg in ss.messages:
        with st.chat_message(msg['role'],avatar='🎓' if msg['role']=='assistant' else None):
            st.write(msg['content'])
            if msg.get('source'):st.caption(msg['source'])
    typed=st.chat_input('اسأل مشعل…',max_chars=1200)
    if typed:prompt=typed
    if prompt:
        history=[{'role':m['role'],'content':m['content']} for m in ss.messages[-6:]]
        ss.messages.append({'role':'user','content':prompt})
        with st.chat_message('user'):st.write(prompt)
        with st.chat_message('assistant',avatar='🎓'):
            if quick:answer,source=local_reply(prompt,analysis),'تحليل فوري من درجتي'
            elif time.monotonic()-ss.get('last_api_call',0)<4:answer,source=local_reply(prompt,analysis),'تحليل محلي سريع'
            else:
                ss.last_api_call=time.monotonic()
                with st.spinner('مشعل يجهز لك الرد…'):
                    answer,source,_=reply(prompt,analysis,history,api_key,get_secret('GEMINI_MODEL','gemini-3.6-flash'),online)
            st.write(answer);st.caption(source)
        ss.messages.append({'role':'assistant','content':answer,'source':source})
        ss.messages=ss.messages[-24:]
    if ss.messages and st.button('مسح المحادثة'):ss.messages=[];st.rerun()

def render_guide():
    heading('الجديد صار أوضح.','الحسابات مرتبطة بمصدرها، حتى تعرف شنو الرقم اللي تشوفه.')
    tab1,tab2,tab3=st.tabs(['اللائحة الجديدة','المعدل التراكمي','نظام المسارات'])
    with tab1:
        st.markdown('### من درجة المادة إلى النسبة')
        st.write('1. نجمع درجة المادة من 100.\n2. نحدد شريحة المادة ونقاطها.\n3. نحسب الدرجة الموزونة: (النقاط + 1) × 20 × وزن المادة ÷ 100.\n4. نجمع الدرجات الموزونة ونقسم على مجموع الأوزان، ثم نضرب في 100.')
        st.info('مثال: 90/100 تعطي 3.65 نقطة؛ النسبة المحوّلة للمادة 93%. لذلك الدرجة الخام والنسبة المحوّلة قد تختلفان.')
        st.write('للعام كامل: نطبق التحويل لكل كورس ثم نأخذ متوسط الكورسين. لا نقرب الكسور إلى الشريحة الأعلى. الخصومات الإدارية والغياب وقرارات الاجتياز ليست ضمن الحسبة.')
        st.table([{'من':low,'التصنيف':letter,'النقاط':points,'الوصف':label} for low,letter,points,label in GPA_SCALE])
        st.link_button('افتح اللائحة الرسمية — صفحات 126 إلى 134',SOURCE_URL)
        st.caption('تمت مراجعة المصدر في 19 سبتمبر 2026. درجتي مشروع مستقل؛ سجل الطالب هو المرجع النهائي.')
    with tab2:
        st.markdown('### ثلاث سنوات، هدف واحد')
        st.write('أدخل النسبة النهائية المعتمدة لكل صف: العاشر 10%، الحادي عشر 20%، الثاني عشر 70%.')
        a,b,c=st.columns(3)
        tenth=a.number_input('نسبة العاشر',0.0,100.0,value=None,key='cum10')
        eleventh=b.number_input('نسبة الحادي عشر',0.0,100.0,value=None,key='cum11')
        twelfth=c.number_input('نسبة الثاني عشر',0.0,100.0,value=None,key='cum12')
        if all(v is not None for v in [tenth,eleventh,twelfth]):st.metric('المعدل التراكمي المتوقع',f'{cumulative(tenth,eleventh,twelfth):.2f}%')
        else:st.caption('أكمل النسب الثلاث ليظهر المعدل.')
        st.link_button('مصدر الأوزان — صفحة 134',SOURCE_URL+'#page=134')
    with tab3:
        st.markdown('### هل أنت في مدرسة تطبق نظام المسارات؟')
        st.write('نظام المسارات له لائحة مستقلة. المعدل يعتمد على وحدات المقررات؛ التربية البدنية والاختيار الحر خارج المعدل. لا تستخدم الحاسبة التقليدية أو حاسبة اللائحة العامة بدلًا منه.')
        st.write('في درجتي حاليًا: شرح الفرق فقط. حاسبة وحدات المسارات غير متاحة حتى تكتمل مراجعة جداولها وضوابطها.')
        st.link_button('اقرأ إعلان وزارة التربية عن لائحة المسارات','https://www2.moe.edu.kw/news/1343')

def render_about():
    heading('من سؤال طالب… إلى درجتي.','مشروع بايثون من خلف الصقري · ZOLD')
    st.markdown('### ليش سويت درجتي؟')
    st.write('كنت أبي طريقة أفهم فيها نسبتي وأثر كل درجة. ومع تغيّر طريقة الحساب، صار هدفي أوضح: أجمع الحسبة، التفسير، والخطوة القادمة في تجربة واحدة للطالب.')
    st.markdown('### خلف نواف خلف الصقري')
    st.write('طالب ومهتم بالبرمجة وصناعة المحتوى. بدأت بتعلم HTML وCSS، وشاركت مع CODED في الأمن السيبراني، والمواقع مع الذكاء الاصطناعي، ثم بايثون مع الذكاء الاصطناعي؛ ومنها بدأ مشروع درجتي.')
    st.markdown('### شلون يشتغل؟')
    st.write('بايثون يحسب ويحلل الدرجات. Streamlit يقدم الواجهة، وPillow يصنع بطاقة النتيجة. مشعل يجمع تحليلًا محليًا سريعًا ومحادثة اختيارية باستخدام Gemini. الحسابات لا تعتمد على إجابة الذكاء الاصطناعي.')
    st.caption('تم تطوير المشروع بمساعدة أدوات الذكاء الاصطناعي، مع مراجعة الحسابات ومصادرها واختبارها. درجتي غير تابع لوزارة التربية.')

{'الرئيسية':render_home,'الحاسبة':render_calculator,'نتيجتي':render_result,'مشعل':render_chat,'الدليل':render_guide,'عن درجتي':render_about}[ss.page]()
st.markdown('<div class="footer">درجتي · صنعه خلف الصقري ضمن الكويت تبرمج<br>أداة تخطيط مستقلة، وليست خدمة رسمية من وزارة التربية. بيانات الجلسة لا تُحفظ في قاعدة بيانات.</div>',unsafe_allow_html=True)
st.button('بدء تجربة جديدة / مسح بيانات الجلسة',on_click=new_visitor,key='reset_all')
