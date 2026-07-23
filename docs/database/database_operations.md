# Reference

## Configuration Matrix

Create Engine Support Functions by Database Type Confirmed by testing [SQLite, PostgreSQL, MSSQL] To Be Tested [MySQL, Oracle] and should be considered experimental.

| Option        | SQLite | PostgreSQL | MySQL | Oracle | MSSQL |
|---------------|--------|------------|-------|--------|-------|
| echo          | Yes    | Yes        | Yes   | Yes    | Yes   |
| future        | Yes    | Yes        | Yes   | Yes    | Yes   |
| pool_pre_ping | Yes    | Yes        | Yes   | Yes    | Yes   |
| pool_size     | No     | Yes        | Yes   | Yes    | Yes   |
| max_overflow  | No     | Yes        | Yes   | Yes    | Yes   |
| pool_recycle  | Yes    | Yes        | Yes   | Yes    | Yes   |
| pool_timeout  | No     | Yes        | Yes   | Yes    | Yes   |

In addition to the dialect-specific options above, the following `create_async_engine` options are accepted regardless of dialect: `connect_args`, `execution_options`, `isolation_level`, `query_cache_size`, and `hide_parameters`. Use `connect_args` for driver-level options such as SSL/TLS settings or connect timeouts.

::: dsg_lib.async_database_functions.database_operations
    handler: python
