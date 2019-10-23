import sqlite3
import config


class sqliteManager:
    total_connections = 0
    conn = None

    def connect():
        if sqliteManager.conn is None:
            sqliteManager.conn = sqlite3.connect(config.DATABASE)
        if not sqliteManager.total_connections:
            res = sqliteManager.conn.execute('SELECT * FROM account_types')
            if res.fetchone() is None:
                sqliteManager.init_db()
        sqliteManager.total_connections += 1

    def close(exception=None):
        if sqliteManager.conn is not None:
            sqliteManager.conn.close()
            sqliteManager.conn = None

    def init_db():
        print("First time running db, initializing some tables")
        queries = []
        table = 'course_roles'
        names = ['student', 'staff']
        for name in names:
            queries.append((table, [name], ['name']))

        table = 'account_types'
        names = ['student', 'course_admin', 'supervisor']
        for name in names:
            queries.append((table, [name], ['name']))

        table = 'file_types'
        names = ['.pdf', '.txt', '.zip', '.tar']
        for name in names:
            queries.append((table, [name], ['name']))

        table = 'marking_methods'
        names = ['text submission', 'file submission']
        for name in names:
            queries.append((table, [name], ['name']))

        table = 'request_statuses'
        names = [
            'pending', 'approved', 'rejected',
            'marked', 'pending mark', 'cancelled'
        ]
        for name in names:
            queries.append((table, [name], ['name']))

        sqliteManager.insert_multiple(queries)

    # inserts 1 row in db
    # table = string, all others are lists

    def insert_single(table, values, columns):
        placeholder = ','.join('?' * len(values))
        if columns is None:
            res = sqliteManager.conn.execute(
                f'INSERT INTO {table} VALUES ({placeholder})',
                values
            )
        else:
            columns = ','.join(columns)
            res = sqliteManager.conn.execute(
                f'INSERT INTO {table} ({columns}) VALUES ({placeholder})',
                values
            )
        sqliteManager.conn.commit()

    # inserts all in list before commit
    # each item in the list should follow
    # same format as insert_single

    def insert_multiple(inserts):
        for table, values, columns in inserts:
            placeholder = ','.join('?' * len(values))
            if columns is None:
                res = sqliteManager.conn.execute(
                    f'INSERT INTO {table} VALUES ({placeholder})',
                    values
                )
            else:
                columns = ','.join(columns)
                res = sqliteManager.conn.execute(
                    f'INSERT INTO {table} ({columns}) VALUES ({placeholder})',
                    values
                )
        sqliteManager.conn.commit()

    # updates all specified columns
    # where clause is only joined by AND
    # table = string, all others are lists

    def update_rows(table, values, columns, where_col, where_val):
        column_placeholder = ' = ? ,'.join(columns) + ' = ? '
        where_placeholder = ' = ? AND '.join(where_col) + ' = ?'
        res = sqliteManager.conn.execute(
            f'UPDATE {table} SET {column_placeholder} \
                WHERE {where_placeholder}',
            values + where_val
        )
        sqliteManager.conn.commit()

    # deletes all specified columns
    # where clause is only joined by AND
    # table = string, all others are lists

    def delete_rows(table, where_col, where_val):
        placeholder = ' = ? AND '.join(where_col) + ' = ?'
        res = sqliteManager.conn.execute(
            f'DELETE FROM {table} WHERE {placeholder}', where_val
        )
        sqliteManager.conn.commit()

    # executes all deletes in list before commit
    # format for each item in list is
    # same as delete_rows

    def delete_multiple(deletes):
        for table, where_col, where_val in deletes:
            placeholder = ' = ? AND '.join(where_col) + ' = ?'
            res = sqliteManager.conn.execute(
                f'DELETE FROM {table} WHERE {placeholder}', where_val
            )
        sqliteManager.conn.commit()

    # returns all specified columns
    # where clause is only joined by AND
    # table = string, all others are lists

    def select_columns(table, columns, where_col, where_val):
        columns = ','.join(columns)
        if where_col is not None:
            placeholder = ' = ? AND '.join(where_col) + ' = ?'
            res = sqliteManager.conn.execute(
                f'SELECT {columns} FROM {table} WHERE {placeholder}',
                where_val
            )
        else:
            res = sqliteManager.conn.execute('SELECT {columns} FROM {table}')
        return res.fetchall()

    # runs a custom SQLite query

    def customQuery(query):
        res = sqliteManager.conn.execute(query)
        return res.fetchall()
