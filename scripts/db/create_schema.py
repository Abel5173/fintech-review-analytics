import sys
import os
import oracledb
import logging

project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.db.oracle_config import ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN

# Set up logging
logging.basicConfig(
    filename="logs/create_schema.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def create_tables():
    # Debug print to verify credentials
    print(f"ORACLE_USER: {ORACLE_USER}")
    print(f"ORACLE_DSN: {ORACLE_DSN}")
    logging.info(
        f"Attempting connection with USER={ORACLE_USER}, DSN={ORACLE_DSN}")

    try:
        conn = oracledb.connect(
            user=ORACLE_USER,
            password=ORACLE_PASSWORD,
            dsn=ORACLE_DSN
            # mode=oracledb.AUTH_MODE_SYSDBA  # Uncomment only if using SYS user
        )
        cursor = conn.cursor()

        # Drop existing tables if they exist
        for table_name in ['banks', 'reviews']:
            try:
                cursor.execute(f"DROP TABLE {table_name} CASCADE CONSTRAINTS")
                print(f"✅ Dropped existing table: {table_name}")
                logging.info(f"Dropped existing table: {table_name}")
            except oracledb.Error as e:
                error, = e.args
                if "ORA-00942" in error.message:  # Table does not exist
                    print(
                        f"ℹ️ Table {table_name} does not exist, skipping drop")
                    logging.info(
                        f"Table {table_name} does not exist, skipping drop")
                else:
                    raise

        with open("scripts/db/schema.sql", "r") as f:
            sql_content = f.read()
            sql_commands = [cmd.strip()
                            for cmd in sql_content.split(";") if cmd.strip()]
            for cmd in sql_commands:
                print(f"Executing:\n{cmd}")
                logging.info(f"Executing SQL: {cmd}")
                cursor.execute(cmd)
                print(f"✅ Executed:\n{cmd}")

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Tables created successfully")
        logging.info("Tables created successfully")

    except oracledb.Error as e:
        error, = e.args
        print(f"❌ Database error: {error.message}")
        logging.error(f"Database error: {error.message}")
    except FileNotFoundError:
        print("❌ Schema file 'scripts/db/schema.sql' not found")
        logging.error("Schema file 'scripts/db/schema.sql' not found")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        logging.error(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    create_tables()
