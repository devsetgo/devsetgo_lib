# Reference

## Supported Databases

| Database      | Library (with link)                                                                 | Supported Database Versions (via library)      |
|---------------|-------------------------------------------------------------------------------------|-----------------------------------------------|
| PostgreSQL    | [asyncpg](https://pypi.org/project/asyncpg/) `>=0.21.0`<br>[SQLAlchemy](https://pypi.org/project/SQLAlchemy/) `>=2.0.10,<2.0.99` | asyncpg supports PostgreSQL 9.2+              |
| SQLite        | [aiosqlite](https://pypi.org/project/aiosqlite/) `>=0.17.0`<br>[SQLAlchemy](https://pypi.org/project/SQLAlchemy/) `>=2.0.10,<2.0.99` | SQLite 3.x                                    |
| Oracle        | [oracledb](https://pypi.org/project/oracledb/) `>=2.4.1,<2.5.0`<br>[SQLAlchemy](https://pypi.org/project/SQLAlchemy/) `>=2.0.10,<2.0.99` | Oracle Database 11.2+                         |
| MS SQL Server | [aioodbc](https://pypi.org/project/aioodbc/) `>=0.4.1`<br>[SQLAlchemy](https://pypi.org/project/SQLAlchemy/) `>=2.0.10,<2.0.99` | SQL Server 2008+ (via ODBC driver)            |
| CockroachDB   | [sqlalchemy-cockroachdb](https://pypi.org/project/sqlalchemy-cockroachdb/) `<2.0.2`<br>[SQLAlchemy](https://pypi.org/project/SQLAlchemy/) `>=2.0.10,<2.0.99`<br>[asyncpg](https://pypi.org/project/asyncpg/) `>=0.21.0` | CockroachDB v19.2+                            |
| MySQL         | [asyncmy](https://pypi.org/project/asyncmy/) `>=0.2.10`<br>[SQLAlchemy](https://pypi.org/project/SQLAlchemy/) `>=2.0.10,<2.0.99` | MySQL 5.7+, MariaDB 10.2+                     |

::: dsg_lib.async_database_functions.database_config
    handler: python
