"""Synthetic local UI fixture. No real correspondent or provider contacted."""
import json,sys
from test_human_verification import HumanComparison
from human_verification_ui import ConfirmationUI
f=HumanComparison();f.setUp();ui=None
try:
    session=f.session();ui=ConfirmationUI(f.identity.db.execute('PRAGMA database_list').fetchone()[2],account='local-test-profile',local_principal=f.f.devices[1]['principal'],session=session['session'],comparison=session['comparison'],time=f.f.time,not_before=f.f.time['earliest'],not_after=str(int(f.f.time['latest'])+600),continuity='ordinary-authorized-descendants').start()
    print(json.dumps(dict(url=ui.url,comparison=session['comparison'])),flush=True)
    for line in sys.stdin:
        if line.strip()=='status':print(json.dumps(dict(evidence=f.identity.db.execute('SELECT count(*) FROM human_verification_evidence').fetchone()[0])),flush=True)
        else:break
finally:
    if ui:ui.close()
    f.tearDown()
