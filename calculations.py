"""Pure Python calculations, independent of the interface and AI.

2026 source: Ministry of Education comprehensive regulations, pp. 126-128,
132 and 134. Decimal marks are classified by their lower boundary, without
rounding up. Administrative deductions are outside this planning calculator.
"""
from math import isfinite
from subjects import GRADES

SOURCE_URL = 'https://www.moe.edu.kw/shorturl/taleem2026-doc'
GPA_SCALE = [
    (97, 'A+', 4.0, 'ممتاز مرتفع'), (94, 'A', 3.8, 'ممتاز'),
    (90, 'A-', 3.65, 'ممتاز منخفض'), (87, 'B+', 3.45, 'جيد جدًا مرتفع'),
    (84, 'B', 3.3, 'جيد جدًا'), (80, 'B-', 3.15, 'جيد جدًا منخفض'),
    (77, 'C+', 2.95, 'جيد مرتفع'), (74, 'C', 2.8, 'جيد'),
    (70, 'C-', 2.65, 'جيد منخفض'), (67, 'D+', 2.45, 'مقبول مرتفع'),
    (64, 'D', 2.3, 'مقبول'), (60, 'D-', 2.15, 'مقبول منخفض'),
    (50, 'E', 1.95, 'مجتاز'), (0, 'F', 0.0, 'راسب'),
]

def valid_number(value, maximum=100):
    if value is None:
        raise ValueError('أكمل جميع الدرجات أولًا؛ الخانة الفارغة ليست صفرًا.')
    value = float(value)
    if not isfinite(value) or not 0 <= value <= maximum:
        raise ValueError(f'الدرجة يجب أن تكون بين 0 و {maximum:g}.')
    return value

def gpa_band(score):
    score = valid_number(score)
    return next((letter, points, label) for lower, letter, points, label in GPA_SCALE if score >= lower)

def practical(name):
    return name in {'الحاسوب', 'المعلوماتية', 'التربية البدنية'} or name.startswith('اختيار حر')

def subjects_for(grade, system='legacy'):
    replacements = {'الحاسوب': 'المعلوماتية', 'تاريخ الكويت': 'الاجتماعيات',
                    'الرياضيات والإحصاء': 'الإحصاء',
                    'مبادئ التفكير الفلسفي / علم النفس والاجتماع': 'مبادئ علم النفس والاجتماع'}
    return [(replacements.get(n, n) if system == 'new' else n, w) for n, w in GRADES[grade]]

def analyze(grade, values, system='legacy', course='الكورس الأول', second=None, name='', demo=False):
    rows = []
    for subject, weight in subjects_for(grade, system):
        maximum = 100 if system == 'new' else weight
        raw = valid_number(values.get(subject), maximum)
        raw2 = valid_number(second.get(subject), maximum) if second is not None else None
        if system == 'new':
            letter, points, label = gpa_band(raw)
            # Apply the published conversion per term, then average the terms.
            converted = (points + 1) * 20
            points2 = gpa_band(raw2)[1] if raw2 is not None else None
            if points2 is not None:
                converted = (converted + (points2 + 1) * 20) / 2
            earned = converted * weight / 100
            raw_pct = (raw + raw2) / 2 if raw2 is not None else raw
            row_gpa = (points + points2) / 2 if points2 is not None else points
        else:
            earned = (raw + raw2) / 2 if raw2 is not None else raw
            raw_pct = earned / weight * 100
            row_gpa, letter, label = None, '', ''
        rows.append(dict(name=subject, score=earned, max_score=weight,
                         percentage=raw_pct, raw=raw, raw2=raw2, gpa=row_gpa,
                         letter=letter, label=label, below_threshold=raw_pct < 50))
    total = sum(r['max_score'] for r in rows)
    pct = sum(r['score'] for r in rows) / total * 100
    return dict(grade=grade, course=course, system=system, subject_results=rows,
                overall_pct=pct, total_score=sum(r['score'] for r in rows), total_max=total,
                gpa=(sum(r['gpa'] * r['max_score'] for r in rows) / total if system == 'new' else None),
                failing=[r['name'] for r in rows if r['below_threshold']],
                student_name=name.strip()[:50], demo=demo,
                tier='قراءة تخطيطية للدرجات', annual=second is not None)

def cumulative(tenth, eleventh, twelfth):
    return valid_number(tenth) * .1 + valid_number(eleventh) * .2 + valid_number(twelfth) * .7

def target_gap(analysis, target):
    target = valid_number(target)
    return max(0, (target - analysis['overall_pct']) * analysis['total_max'] / 100)

def next_steps(analysis):
    rows = sorted(analysis['subject_results'], key=lambda r: r['percentage'])
    recommendations = []
    for row in rows:
        if analysis['system'] == 'new' and not analysis.get('annual'):
            higher = sorted([b for b in GPA_SCALE if b[0] > row['raw']], key=lambda b: b[0])
            if higher:
                lower, letter, points, _ = higher[0]
                gain = (points - row['gpa']) * 20 * row['max_score'] / analysis['total_max']
                recommendations.append(dict(name=row['name'], need=lower-row['raw'], gain=gain, goal=letter))
        elif analysis['system'] == 'legacy':
            room = row['max_score'] - row['score']
            if room > 0:
                amount = min(5, room)
                recommendations.append(dict(name=row['name'], need=amount,
                                            gain=amount / analysis['total_max'] * 100, goal='تحسين'))
    return recommendations
