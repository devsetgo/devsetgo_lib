## Database queries covered by tests

This page lists, function-by-function, which query patterns are exercised by the automated test suite. It’s meant to give users of the library a clear picture of what’s verified in CI, especially for the enhanced execute_one and execute_many APIs.

Context
- Runtime/driver in tests: SQLite (aiosqlite), in-memory shared cache
- ORM: SQLAlchemy Async (Core and ORM)
- Result shaping rules validated by tests:
	- SELECT with one column → list of scalars
	- SELECT with multiple columns → list of dicts (column name → value)
	- SELECT with ORM entity → list of ORM objects
	- For DML with RETURNING (backend-dependent): rows appear in metadata when present

Note: Some branches are validated via lightweight mocks to assert fallback behavior when drivers return different row shapes.

---

## execute_one(query, values=None, return_metadata=False)

Tested SELECT paths
- ORM SELECT(User) returns a list of ORM objects.
- Text SELECT single column returns scalars in metadata when return_metadata=True.
- Text SELECT multiple columns returns list of dicts in metadata when return_metadata=True.
- Row-shaping fallbacks via mocks:
	- keys-present, mapping with one key → rows as scalars
	- keys-present, objects with __dict__ → rows contain objects
	- keys-present, plain objects → rows contain objects
	- no-keys path, mapping with one key → rows as scalars
	- no-keys path, mapping with multiple keys → rows as dicts
	- no-keys path, __dict__ and plain object branches

Tested DML paths
- INSERT (ORM/Core) with default behavior returns "complete" (backward compatible).
- UPDATE and DELETE with return_metadata=True return metadata including rowcount (driver differences tolerated as 0/1 in CI).
- Text INSERT duplicate (violates unique) triggers handled IntegrityError → error dict.
- Rows in metadata when statement returns rows: behavior implemented; RETURNING scenarios are backend-dependent (not asserted under SQLite).

Error handling
- General exception path via mocked session → error dict.

Transaction
- Commit occurs for DML; explicit verification is implicit through state checks in subsequent SELECTs.

---

## execute_many(queries, return_results=False)

Tested mixed-batch behavior
- Batch with multiple statements in order: INSERT, INSERT, SELECT (ORM scalar), text COUNT(*), UPDATE, text DELETE.
- With return_results=True:
	- INSERT entries return metadata dicts with rowcount and (if provided by driver) inserted_primary_key.
	- ORM SELECT entries delegate to read_query and return shaped lists (e.g., list of scalars for single-column selects).
	- Text SELECT COUNT(*) returns metadata with rows as a list of scalars (tolerant of 0/1/2 in CI to account for timing/visibility).
	- UPDATE and DELETE entries return metadata dicts with rowcount (tolerant 0/1 in CI).

Tested SELECT (text) shaping inside execute_many
- Text SELECT with multiple columns returns rows as list of dicts in metadata.

Row-shaping fallbacks via mocks
- keys-present branch:
	- mapping with one key → rows as scalars
	- objects with __dict__ → rows contain objects
	- plain objects → rows contain objects
- no-keys branch:
	- mapping with one key → rows as scalars
	- mapping with multiple keys → rows as dicts
	- __dict__ and plain object branches

Error handling
- Bad SQL in batch returns an error dict.

Legacy return
- When return_results=False (default), returns the string "complete" (backward compatible).

---

## read_query(query)

Entity and scalar columns
- ORM SELECT(User) → list of ORM objects.
- Scalar column DISTINCT → list of unique scalars.
- Multi-column SELECT DISTINCT (e.g., color, name) → validated both as tuples and as dicts depending on shape.

Mapping and fallback behavior
- keys-present, single key → list of scalars via scalars().all().
- keys-present, multi key → list of dicts via row._mapping.
- no-keys fallback:
	- _mapping with one key → list of scalars
	- row.__dict__ present → returns row objects
	- plain row objects → returns row objects

Error handling
- SQLAlchemyError and General Exception paths validated via mocks.

---

## read_multi_query({name: query, ...})

Multiple queries in a dict
- Returns a dict mapping each name to its shaped result list.

Mapping and fallback behavior
- keys-present, single key → scalars list
- keys-present, multi key → list of dicts
- no-keys fallback:
	- _mapping with one key → scalars list
	- row.__dict__ → list of objects
	- plain row objects → list of objects

Error handling
- SQLAlchemyError and General Exception paths validated via mocks.

---

## count_query(select(...))

Behavior
- After seeding many rows, count_query returns the expected count.

Error handling
- SQLAlchemyError and General Exception paths validated via mocks.

---

## read_one_record(select(...))

Behavior
- Returns a single ORM object for a matching row; returns None when no match.

Error handling
- General Exception path validated via mock.

---

## get_table_names()

Behavior
- Returns a list of table names from Base metadata. Test asserts the list exists (other test modules may add tables to the shared Base).

Error handling
- Exception path validated via patched Base.metadata.tables.keys.

---

## get_columns_details(Table)

Behavior
- Returns a dict of column metadata (type, nullable, primary_key, unique, autoincrement, default) for the provided table.

Error handling
- Exception path validated via a FakeTable raising on column access.

---

## get_primary_keys(Table)

Behavior
- Returns a list of primary key column names for the table.

Error handling
- Exception path validated via a FakeTable raising from primary_key.columns.

---

## Deprecated helpers (covered for backward compatibility)

create_one(record)
- Inserts a single record; returns the ORM object. Error paths validated (SQLAlchemyError, IntegrityError, General Exception). Emits DeprecationWarning.

create_many(records)
- Bulk insert list of records; returns list of ORM objects. Error paths validated. Emits DeprecationWarning.

update_one(table, record_id, new_values)
- Updates a single record by PK; returns updated ORM object. Error paths validated (not found, IntegrityError, SQLAlchemyError, General Exception). Emits DeprecationWarning.

delete_one(table, record_id)
- Deletes a single record by PK; success dict on delete; error paths validated (not found, SQLAlchemyError, General Exception). Emits DeprecationWarning.

delete_many(table, id_column_name, id_values)
- Deletes many by IDs; returns number deleted or error dict when invalid column. Emits DeprecationWarning.

---

## Backend notes and caveats
- These tests run under SQLite + aiosqlite. Some behaviors (rowcount, RETURNING) vary by driver/backends (e.g., PostgreSQL). Tests that check rowcount are tolerant (0 or 1) to accommodate these differences in CI.
- RETURNING is supported by the library APIs (rows appear in metadata), but assertions for RETURNING-specific rows are not enforced under SQLite. You can add PostgreSQL-backed tests to validate this further.

---

## At-a-glance (what’s most extensive)
- execute_one: SELECT via ORM and text (single/multi column), DML metadata, robust row-shaping with and without keys, error paths.
- execute_many: Mixed batches with INSERT/SELECT/COUNT/UPDATE/DELETE, text SELECT shaping, extensive row-shaping (keys/no-keys), error paths, legacy and opt-in result modes.

This reflects the test suite as of 2025-08-10.
