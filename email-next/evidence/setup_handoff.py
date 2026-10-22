"""Crash-safe single-copy handoff journal experiment with opaque trusted inputs.

Each local intent key here names one scoped unit. Parent multi-copy planning,
correlation privacy and collectively atomic activation are outside this component.

No actual MLS state installation, secret erasure, authority evaluation or transport.
The generation is a configured stand-in for the owning dependency snapshot; a stored
receipt is an observation supplied by a trusted retirement adapter, not erasure proof.
"""
import sqlite3
from contextlib import contextmanager


class HandoffJournal:
    def __init__(self, path):
        self.db = sqlite3.connect(path, isolation_level=None, timeout=10)
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS dependency(singleton INTEGER PRIMARY KEY CHECK(singleton=1),generation INTEGER NOT NULL);
          INSERT OR IGNORE INTO dependency VALUES(1,0);
          CREATE TABLE IF NOT EXISTS intent(id TEXT NOT NULL,revision INTEGER NOT NULL,content BLOB NOT NULL,cancelled INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(id,revision));
          CREATE TABLE IF NOT EXISTS selected(id TEXT PRIMARY KEY,revision INTEGER NOT NULL,FOREIGN KEY(id,revision) REFERENCES intent(id,revision));
          CREATE TABLE IF NOT EXISTS stage(id TEXT NOT NULL,revision INTEGER NOT NULL,generation INTEGER NOT NULL,checkpoint BLOB NOT NULL,contribution BLOB NOT NULL,deliveries BLOB NOT NULL,retirement BLOB,active INTEGER NOT NULL DEFAULT 0,PRIMARY KEY(id,revision),FOREIGN KEY(id,revision) REFERENCES intent(id,revision));
        ''')

    def close(self):
        self.db.close()

    @contextmanager
    def transaction(self):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            yield
            self.db.commit()
        except BaseException:
            self.db.rollback()
            raise

    def freeze(self, intent, revision, content):
        if not isinstance(intent,str) or not intent or type(revision) is not int or revision < 1 or type(content) is not bytes:
            raise ValueError('Trusted local intent/revision/content required')
        with self.transaction():
            old = self.db.execute('SELECT content FROM intent WHERE id=? AND revision=?',(intent,revision)).fetchone()
            if old is not None:
                if old[0] != content:
                    raise ValueError('Immutable intent revision')
                return
            selected = self.db.execute('SELECT revision FROM selected WHERE id=?',(intent,)).fetchone()
            if selected and revision <= selected[0]:
                raise ValueError('New revision must advance selection')
            self.db.execute('UPDATE intent SET cancelled=1 WHERE id=?',(intent,))
            self.db.execute('INSERT INTO intent(id,revision,content) VALUES(?,?,?)',(intent,revision,content))
            self.db.execute('INSERT INTO selected VALUES(?,?) ON CONFLICT(id) DO UPDATE SET revision=excluded.revision',(intent,revision))

    def _selected(self, intent, revision):
        if self.db.execute('SELECT 1 FROM selected s JOIN intent i ON i.id=s.id AND i.revision=s.revision WHERE i.id=? AND i.revision=? AND i.cancelled=0',(intent,revision)).fetchone() is None:
            raise ValueError('Cancelled or superseded intent')

    def generation(self):
        return self.db.execute('SELECT generation FROM dependency WHERE singleton=1').fetchone()[0]

    def advance_dependency(self):
        with self.transaction():
            self.db.execute('UPDATE dependency SET generation=generation+1 WHERE singleton=1')

    def stage(self, intent, revision, generation, checkpoint, contribution, deliveries, *, _before_commit=None):
        if type(generation) is not int or generation < 0 or not all(type(v) is bytes and v for v in (checkpoint,contribution,deliveries)):
            raise ValueError('Opaque trusted preparation required')
        with self.transaction():
            self._selected(intent,revision)
            if self.generation() != generation:
                raise ValueError('Changed preparation dependencies')
            retained = self.db.execute('SELECT generation,checkpoint,contribution,deliveries FROM stage WHERE id=? AND revision=?',(intent,revision)).fetchone()
            expected = (generation,checkpoint,contribution,deliveries)
            if retained is not None:
                if retained != expected:
                    raise ValueError('Immutable staged preparation')
                return
            self.db.execute('INSERT INTO stage(id,revision,generation,checkpoint,contribution,deliveries) VALUES(?,?,?,?,?,?)',(intent,revision,*expected))
            if _before_commit:
                _before_commit()

    def retirement_complete(self, intent, revision, receipt):
        if type(receipt) is not bytes or not receipt:
            raise ValueError('Trusted retirement observation required')
        # Cleanup completion is recorded even when later authority/cancellation
        # holds activation. It cannot be undone to recreate consumed secrets.
        with self.transaction():
            row = self.db.execute('SELECT retirement FROM stage WHERE id=? AND revision=?',(intent,revision)).fetchone()
            if row is None:
                raise ValueError('Unknown stage')
            if row[0] is not None and row[0] != receipt:
                raise ValueError('Different retirement observation')
            self.db.execute('UPDATE stage SET retirement=? WHERE id=? AND revision=?',(receipt,intent,revision))

    def activate(self, intent, revision, *, _before_commit=None):
        with self.transaction():
            self._selected(intent,revision)
            row = self.db.execute('SELECT generation,retirement FROM stage WHERE id=? AND revision=?',(intent,revision)).fetchone()
            if row is None or row[1] is None:
                raise ValueError('Retirement incomplete')
            if row[0] != self.generation():
                raise ValueError('Changed handoff dependencies')
            # The single stage row is both retained handoff result and outbox
            # activation; there is no second independently committed enqueue.
            self.db.execute('UPDATE stage SET active=1 WHERE id=? AND revision=?',(intent,revision))
            if _before_commit:
                _before_commit()

    def cancel(self, intent, revision):
        with self.transaction():
            self.db.execute('UPDATE intent SET cancelled=1 WHERE id=? AND revision=?',(intent,revision))

    def inspect(self, intent, revision):
        row = self.db.execute('SELECT generation,checkpoint,contribution,deliveries,retirement,active FROM stage WHERE id=? AND revision=?',(intent,revision)).fetchone()
        return row

    def inspect_eligible(self):
        # Inspection only: this is not an exclusive transport claim or a final
        # current identity/clock/route/policy/SMTP authorization decision.
        return self.db.execute('SELECT t.id,t.revision,t.contribution,t.deliveries FROM stage t JOIN selected s ON s.id=t.id AND s.revision=t.revision JOIN intent i ON i.id=t.id AND i.revision=t.revision WHERE t.active=1 AND i.cancelled=0 AND t.generation=(SELECT generation FROM dependency WHERE singleton=1)').fetchall()
