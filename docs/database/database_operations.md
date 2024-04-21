# Reference

## Configuration Matrix

Create Engine Support Functions by Database Type Confirmed by testing [SQLITE, PostgreSQL] To Be Tested [MySQL, Oracle, MSSQL] and should be considered experimental.

| Option        | SQLite | PostgreSQL | MySQL | Oracle | MSSQL |
|---------------|--------|------------|-------|--------|-------|
| echo          | Yes    | Yes        | Yes   | Yes    | Yes   |
| future        | Yes    | Yes        | Yes   | Yes    | Yes   |
| pool_pre_ping | Yes    | Yes        | Yes   | Yes    | Yes   |
| pool_size     | No     | Yes        | Yes   | Yes    | Yes   |
| max_overflow  | No     | Yes        | Yes   | Yes    | Yes   |
| pool_recycle  | Yes    | Yes        | Yes   | Yes    | Yes   |
| pool_timeout  | No     | Yes        | Yes   | Yes    | Yes   |


::: dsg_lib.async_database_functions.database_operations
    handler: python
