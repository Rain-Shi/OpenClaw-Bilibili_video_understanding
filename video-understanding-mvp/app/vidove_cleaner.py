from __future__ import annotations

import re


_TRAD_TO_SIMP = {
    '這': '这', '於': '于', '產': '产', '還': '还', '網': '网', '擁': '拥', '與': '与', '點': '点',
    '臨': '临', '搗': '捣', '裏': '里', '現': '现', '鏽': '锈', '蒼': '苍', '圍': '围', '這批': '这批',
    '劣質': '劣质', '瓊': '琼', '個': '个', '獲': '获', '顯': '显', '過': '过', '萬': '万', '幣': '币',
    '買': '买', '賣': '卖', '連同': '连同', '達': '达', '牽': '牵', '廣': '广', '臺': '台', '灣': '湾',
    '價': '价', '體': '体', '們': '们', '對': '对', '為': '为', '廣東': '广东', '聲稱': '声称',
    '創辦': '创办', '現場': '现场', '號': '号'
}

_EDITORIAL_PATTERNS = [
    r'^The translated text is already in Chinese',
    r'^No revision is needed\.?$',
    r'^A total of \d+ people were arrested\.?$',
    r'^The other \d+ are still at large\.?$',
    r'^The amount involved reached over',
]


def normalize_script(text: str) -> str:
    s = (text or '').strip()
    for trad, simp in _TRAD_TO_SIMP.items():
        s = s.replace(trad, simp)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def looks_like_editorial_leak(text: str) -> bool:
    t = (text or '').strip()
    if not t:
        return True
    return any(re.search(p, t, re.IGNORECASE) for p in _EDITORIAL_PATTERNS)


def is_mostly_ascii(text: str) -> bool:
    t = (text or '').strip()
    if not t:
        return False
    ascii_chars = sum(1 for c in t if ord(c) < 128)
    return ascii_chars / max(len(t), 1) > 0.8


def contains_cjk(text: str) -> bool:
    return any('\u4e00' <= ch <= '\u9fff' for ch in (text or ''))
