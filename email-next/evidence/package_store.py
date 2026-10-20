"""SQLite allocation experiment; identities and package references must be prevalidated."""
import sqlite3
from contextlib import contextmanager

class PackageStore:
    def __init__(self, path):
        self.db = sqlite3.connect(path, timeout=10, isolation_level=None)
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS packages (
                reference TEXT PRIMARY KEY,
                device TEXT NOT NULL,
                profile TEXT NOT NULL,
                allocated INTEGER NOT NULL DEFAULT 0 CHECK(allocated IN (0,1))
            );
            CREATE TABLE IF NOT EXISTS requests (
                principal TEXT NOT NULL,
                device TEXT NOT NULL,
                profile TEXT NOT NULL,
                request TEXT NOT NULL,
                package TEXT UNIQUE REFERENCES packages(reference),
                PRIMARY KEY(principal,device,profile,request)
            );
        ''')

    def close(self):
        self.db.close()

    @staticmethod
    def _strings(*values):
        if not all(isinstance(value, str) and value for value in values):
            raise ValueError('Nonempty scoped identifiers required')

    @contextmanager
    def _transaction(self):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            yield
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def publish(self, reference, device, profile):
        self._strings(reference, device, profile)
        # A previously allocated package cannot be recycled through publication.
        with self._transaction():
            self.db.execute('INSERT INTO packages(reference,device,profile) VALUES(?,?,?)',
                            (reference, device, profile))

    def allocate(self, principal, device, profile, request):
        self._strings(principal, device, profile, request)
        scope = (principal, device, profile, request)
        with self._transaction():
            previous = self.db.execute('''SELECT package FROM requests
                WHERE principal=? AND device=? AND profile=? AND request=?''', scope).fetchone()
            if previous is not None:
                package = previous[0]
            else:
                available = self.db.execute('''SELECT reference FROM packages
                    WHERE device=? AND profile=? AND allocated=0 ORDER BY reference LIMIT 1''',
                    (device, profile)).fetchone()
                package = available[0] if available else None
                if package is not None:
                    self.db.execute('UPDATE packages SET allocated=1 WHERE reference=?', (package,))
                self.db.execute('''INSERT INTO requests(principal,device,profile,request,package)
                    VALUES(?,?,?,?,?)''', (*scope, package))
        # No allocation is exposed before its transaction commits.
        return {'state': 'depleted'} if package is None else {
            'state': 'allocated', 'packageReference': package}
