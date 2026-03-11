from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

from .models import TimelineUnit, UnderstandingResult
from .vidove_cleaner import looks_like_editorial_leak

ENTITY_STOPWORDS = {
    '警方', '女人', '男人', '视频', '故事', '品牌', '东西', '自己', '他们', '我们', '你们',
    '今天', '这个', '那个', '这里', '那里', '因为', '所以', '然后', '如果', '但是', '只是',
}


@dataclass
class EntityNode:
    id: str
    label: str
    type: str
    aliases: list[str] = field(default_factory=list)
    descriptions: list[str] = field(default_factory=list)
    mention_count: int = 0
    salience: float = 0.0
    confidence: float = 0.0


@dataclass
class RelationEdge:
    source: str
    predicate: str
    target: str
    confidence: float = 0.0
    evidence: list[str] = field(default_factory=list)


@dataclass
class EntityGraph:
    entities: list[EntityNode]
    relations: list[RelationEdge]
    open_questions: list[str]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            'entities': [asdict(x) for x in self.entities],
            'relations': [asdict(x) for x in self.relations],
            'open_questions': self.open_questions,
            'notes': self.notes,
        }

    def to_prompt_text(self) -> str:
        lines: list[str] = ['Entities:']
        for ent in self.entities[:12]:
            alias_text = f" aliases={','.join(ent.aliases[:3])}" if ent.aliases else ''
            desc = ('；'.join(ent.descriptions[:2]) if ent.descriptions else '').strip()
            lines.append(f"- {ent.label} [{ent.type}] mention_count={ent.mention_count} salience={ent.salience:.2f}{alias_text} {desc}".strip())
        lines.append('Relations:')
        for rel in self.relations[:12]:
            lines.append(f"- {rel.source} --{rel.predicate}--> {rel.target} (conf={rel.confidence:.2f})")
        lines.append('Open questions:')
        for q in self.open_questions[:6]:
            lines.append(f'- {q}')
        return '\n'.join(lines)[:3600]


def _extract_candidates(text: str) -> list[str]:
    if not text or looks_like_editorial_leak(text):
        return []
    candidates = re.findall(r'[A-Z][A-Za-z0-9_\-]{1,}|[\u4e00-\u9fff]{2,8}', text)
    out: list[str] = []
    for cand in candidates:
        if cand in ENTITY_STOPWORDS:
            continue
        if cand.isdigit():
            continue
        if len(cand.strip()) < 2:
            continue
        if cand not in out:
            out.append(cand)
    return out


def _classify_entity(label: str) -> str:
    if any(s in label for s in ['案', '事件', '调查', '品牌']):
        return 'case_or_event'
    if any(s in label for s in ['总裁', '经理', '队长']):
        return 'person'
    if any(s in label for s in ['公式', '定律', '定理', '函数', '算法', '模型', '参数']):
        return 'concept'
    if any(s in label for s in ['公司', '集团', '品牌', '大学']):
        return 'organization'
    return 'entity'


def build_entity_graph(result: UnderstandingResult) -> EntityGraph:
    counts: dict[str, int] = {}
    evidences: dict[str, list[str]] = {}
    for unit in result.timeline:
        text = (unit.speech or '').strip()
        if not text:
            continue
        for cand in _extract_candidates(text):
            counts[cand] = counts.get(cand, 0) + 1
            evidences.setdefault(cand, [])
            if len(evidences[cand]) < 2 and text not in evidences[cand]:
                evidences[cand].append(text)

    ranked = sorted(counts.items(), key=lambda kv: (kv[1], len(kv[0])), reverse=True)
    entities: list[EntityNode] = []
    id_by_label: dict[str, str] = {}
    for idx, (label, count) in enumerate(ranked[:12], start=1):
        ent = EntityNode(
            id=f'ent_{idx:03d}',
            label=label,
            type=_classify_entity(label),
            aliases=[],
            descriptions=evidences.get(label, [])[:2],
            mention_count=count,
            salience=min(1.0, count / 6.0),
            confidence=min(0.95, 0.4 + count * 0.08),
        )
        entities.append(ent)
        id_by_label[label] = ent.id

    relations: list[RelationEdge] = []
    relation_keys: set[tuple[str, str, str]] = set()
    for unit in result.timeline:
        text = (unit.speech or '').strip()
        cands = [c for c in _extract_candidates(text) if c in id_by_label]
        if len(cands) >= 2:
            a, b = cands[0], cands[1]
            pred = 'related_to'
            if any(k in text for k in ['是', '叫', '身份', '总裁', '经理']):
                pred = 'introduced_as'
            elif any(k in text for k in ['同一个人', '就是', '其实是']):
                pred = 'possibly_same_as'
            key = (a, pred, b)
            if key not in relation_keys:
                relation_keys.add(key)
                relations.append(RelationEdge(source=a, predicate=pred, target=b, confidence=0.55, evidence=[text]))

    open_questions: list[str] = []
    summary_agent = (result.metadata or {}).get('summary_agent') or {}
    for item in (summary_agent.get('uncertain_points') or [])[:6]:
        if item not in open_questions:
            open_questions.append(item)

    notes = ['Lightweight offline entity graph derived from timeline text only.']
    return EntityGraph(entities=entities, relations=relations[:16], open_questions=open_questions, notes=notes)
