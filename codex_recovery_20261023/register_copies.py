import json
import pathlib
import sqlite3


root = pathlib.Path(__file__).resolve().parent
mapping = json.loads((root / 'resume_mapping.json').read_text())
validation = sqlite3.connect('/private/tmp/codex_recovery_native_validation/state_5.sqlite')
validation.row_factory = sqlite3.Row
destination = sqlite3.connect(str(pathlib.Path.home() / '.codex/state_5.sqlite'), timeout=10)
columns = [row[1] for row in destination.execute('pragma table_info(threads)')]
rows = []
for entry in mapping:
    parsed = validation.execute('select * from threads where id=?', (entry['recovered_id'],)).fetchone()
    assert parsed is not None
    row = dict(parsed)
    row['rollout_path'] = entry['native_destination']
    row['history_mode'] = 'legacy'
    row['title'] = entry['title']
    row['first_user_message'] = entry['title']
    row['has_user_event'] = 1
    assert pathlib.Path(row['rollout_path']).is_file()
    rows.append(row)

try:
    destination.execute('begin immediate')
    for row in rows:
        assert not destination.execute('select 1 from threads where id=?', (row['id'],)).fetchone()
    statement = 'insert into threads (' + ','.join(columns) + ') values (' + ','.join('?' for _ in columns) + ')'
    for row in rows:
        destination.execute(statement, [row.get(column) for column in columns])
    destination.commit()
except BaseException:
    destination.rollback()
    raise
print(json.dumps({'registered_new_copies': len(rows), 'existing_records_changed': 0}))
