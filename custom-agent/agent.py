"""Bounded demonstration loop; no tool execution from model text."""
from scripts.llm_example import ask_llm

for round_number in range(2):
    print('Round',round_number+1)
    print(ask_llm('Explain how to check a dealer API change.'))
print('Stop. A human must review the proposal.')
