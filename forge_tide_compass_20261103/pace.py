"""Guard long badge operations against the current authorized work block."""
from pathlib import Path
import json,time
R=Path(__file__).resolve().parent
def work(minutes=0):
 state=json.loads((R/'schedule.json').read_text());now=time.time()
 assert state['status']=='active' and state['phase']=='work','Run is outside its work phase'
 assert now+minutes*60<state['work_until_epoch'],'Save now and honor the scheduled break'
 return state
