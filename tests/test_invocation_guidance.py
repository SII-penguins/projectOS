#!/usr/bin/env python3
"""Static regression checks for ProjectOS trigger and onboarding UX."""
from pathlib import Path
import re, unittest

ROOT=Path(__file__).resolve().parents[1]

class InvocationGuidanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill=(ROOT/'SKILL.md').read_text(encoding='utf-8')
        cls.openai=(ROOT/'agents/openai.yaml').read_text(encoding='utf-8')
        cls.guide=(ROOT/'references/onboarding-and-invocation.md').read_text(encoding='utf-8')
        cls.scenarios=(ROOT/'references/evaluation-scenarios.md').read_text(encoding='utf-8')

    def test_description_contains_natural_chinese_triggers_and_guardrail(self):
        front=self.skill.split('---',2)[1]
        for phrase in ('我想做/开发一个','调研整理成项目计划','TODO/PROGRESS','resume','close out'):
            self.assertIn(phrase,front)
        self.assertIn('Do not invoke for a small standalone code edit',front)
        self.assertIn('user does not need to know internal modes',front)

    def test_first_turn_does_not_expose_mode_menu(self):
        self.assertIn('Do **not** present a mode menu by default',self.skill)
        self.assertIn('ask at most one decision-critical question',self.skill)
        self.assertIn('Do not show these internal route names',self.guide)
        self.assertNotIn('choose Explore, Create, Maintain, Resume, or Closeout',self.openai)

    def test_default_prompt_is_single_front_door(self):
        self.assertIn('$project-os',self.openai)
        self.assertIn('infer the right workflow',self.openai)
        self.assertIn('do not make me choose internal modes',self.openai)

    def test_progressive_gates_and_bounded_interrogation_exist(self):
        for heading in ('Gate 1 — Understand','Gate 2 — Approve the Brief','Gate 3 — Approve the Document Map','Gate 4 — Generate/Reconcile','Gate 5 — Handoff'):
            self.assertIn(heading,self.guide)
        self.assertRegex(self.skill,re.compile(r'no more than five accepted questions',re.I))
        self.assertIn('stop questioning as soon as the current gate can proceed safely',self.skill)

    def test_positive_and_negative_trigger_scenarios_exist(self):
        self.assertIn('Positive implicit triggers',self.scenarios)
        self.assertIn('Negative or lightweight cases',self.scenarios)
        self.assertIn('我想开发一个《某游戏》的 MOD',self.scenarios)
        self.assertIn('把 README 里的一个错别字改掉',self.scenarios)
        self.assertIn('Do not force ProjectOS ceremony',self.scenarios)

if __name__=='__main__': unittest.main()
