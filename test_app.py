import time
from io import BytesIO
import pytest
from PIL import Image
from calculations import *
from certificate import create_result_image
import mishal
from streamlit.testing.v1 import AppTest

GRADE='الصف العاشر'
def marks(value,system='new'):
    return {n:value if system=='new' else w*value/100 for n,w in subjects_for(GRADE,system)}

@pytest.mark.parametrize('score,letter,points',[(100,'A+',4),(97,'A+',4),(96.99,'A',3.8),(94,'A',3.8),(93.99,'A-',3.65),(90,'A-',3.65),(89.99,'B+',3.45),(50,'E',1.95),(49.99,'F',0),(0,'F',0)])
def test_bands(score,letter,points):
    assert gpa_band(score)[:2]==(letter,points)

@pytest.mark.parametrize('value',[None,-1,101,float('nan'),float('inf')])
def test_invalid(value):
    with pytest.raises(ValueError):gpa_band(value)

def test_legacy_and_weights():
    a=analyze(GRADE,marks(80,'legacy'))
    assert a['overall_pct']==pytest.approx(80)
    assert a['total_max']==500
    assert target_gap(a,90)==pytest.approx(50)

def test_new_conversion():
    a=analyze(GRADE,marks(90),'new')
    assert a['gpa']==pytest.approx(3.65)
    assert a['overall_pct']==pytest.approx(93)
    # Annual conversion must average converted terms, not classify raw average.
    a=analyze(GRADE,marks(97),'new',second=marks(89))
    assert a['overall_pct']==pytest.approx((100+89)/2)
    assert a['gpa']==pytest.approx((4+3.45)/2)

def test_zero_is_not_missing():
    a=analyze(GRADE,marks(0),'new')
    assert a['overall_pct']==20 # exact published formula, explicitly disclosed in UI
    assert len(a['failing'])==11
    with pytest.raises(ValueError):analyze(GRADE,{},'new')

def test_cumulative():
    assert cumulative(80,90,100)==96

def test_gain_matches_recalculation():
    values=marks(89)
    a=analyze(GRADE,values,'new')
    step=next_steps(a)[0]
    values[step['name']]+=step['need']
    assert analyze(GRADE,values,'new')['overall_pct']-a['overall_pct']==pytest.approx(step['gain'])

def test_deadline_and_error(monkeypatch):
    def stalled(*args):time.sleep(.4);return 'late'
    monkeypatch.setattr(mishal,'_request',stalled)
    started=time.monotonic()
    answer,source,_=mishal.reply('وين اركز',None,[],'fake',deadline=.02)
    assert time.monotonic()-started<.2
    assert 'محلي' in source and answer
    def failed(*args):raise RuntimeError('do not reveal this')
    monkeypatch.setattr(mishal,'_request',failed)
    assert 'do not reveal' not in mishal.reply('hello',None,[],'fake')[0]

def test_card():
    a=analyze(GRADE,marks(90),'new',name='خلف نواف خلف الصقري')
    image=Image.open(BytesIO(create_result_image(a)))
    assert image.size==(1080,590+11*66+170)

def test_app_demo_navigation_and_reset():
    at=AppTest.from_file('app.py',default_timeout=30).run()
    assert not at.exception
    next(b for b in at.button if b.label=='جرّب بمثال جاهز').click().run()
    assert not at.exception
    assert at.session_state['analysis']['demo']
    at.button(key='nav_مشعل').click().run()
    assert not at.exception
    next(b for b in at.button if b.label=='وين أركز؟').click().run()
    assert not at.exception
    assert at.session_state['messages'][-1]['source']=='تحليل فوري من درجتي'
    at.button(key='nav_الحاسبة').click().run()
    assert at.selectbox(key='grade').value=='الصف الحادي عشر - علمي'
    assert any(n.value==95 for n in at.number_input)
    assert not at.exception
    at.button(key='reset_all').click().run()
    assert at.session_state['analysis'] is None
    assert not at.exception

def test_empty_calculator_and_guide():
    at=AppTest.from_file('app.py',default_timeout=30).run()
    at.button(key='nav_الحاسبة').click().run()
    next(b for b in at.button if b.label=='اعرض نتيجتي ←').click().run()
    assert at.warning and at.session_state['analysis'] is None
    at.button(key='nav_الدليل').click().run()
    assert not at.exception
    at.number_input(key='cum10').set_value(80)
    at.number_input(key='cum11').set_value(90)
    at.number_input(key='cum12').set_value(100).run()
    assert at.metric[0].value=='96.00%'
