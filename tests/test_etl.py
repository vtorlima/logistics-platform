"""
Integration test: seed → XLSX → ETL → PostgreSQL → verify.

Requirements:
  - PostgreSQL running with a 'vctrans_test' database
  - Schema applied: psql -U <user> -d vctrans_test -f database/schema.sql
  - TEST_DATABASE_URL set in .env (e.g. postgresql://user:pw@localhost/vctrans_test)

Run:
  pytest tests/test_etl.py -v
"""

import os
import tempfile
import pytest
import psycopg2
from dotenv import load_dotenv

load_dotenv()

from seed.generators.master_data import (
    generate_empresa,
    generate_passageiro,
    generate_colaboradores,
    generate_frota,
)
from seed.generators.rides import generate_rides
from seed.generators.xlsx_writer import write_workbook
from seed.generators.summaries import (
    generate_folha,
    generate_financeiro,
    generate_frota_stats,
    generate_folga,
    generate_metas,
)
from seed.config import OS_NUMBER_START
from etl.reader import read_workbook
from etl.transformer import transform
from etl.loader import load


TEST_MONTH = "2026-01"


@pytest.fixture(scope="module")
def test_conn():
    """Open a connection to the test database. Skip if TEST_DATABASE_URL is not set."""
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set — skipping integration test")
    conn = psycopg2.connect(url)
    yield conn
    conn.close()


@pytest.fixture(scope="module")
def clean_db(test_conn):
    """Truncate all tables before the test run to ensure a clean state."""
    tables = [
        "rides", "monthly_driver_summary", "monthly_company_summary",
        "monthly_vehicle_summary", "driver_schedule", "rate_history",
    ]
    with test_conn.cursor() as cur:
        for table in tables:
            cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
    test_conn.commit()
    yield


@pytest.fixture(scope="module")
def seed_xlsx(tmp_path_factory):
    """Generate seed data for TEST_MONTH and write to a temp XLSX file."""
    tmp_dir = tmp_path_factory.mktemp("seed_output")

    empresa = generate_empresa()
    passageiro = generate_passageiro()
    colaboradores = generate_colaboradores()
    frota = generate_frota()
    rides = generate_rides(TEST_MONTH, passageiro, OS_NUMBER_START)
    folha = generate_folha(TEST_MONTH, rides)
    financeiro = generate_financeiro(TEST_MONTH, rides)
    frota_stats = generate_frota_stats(TEST_MONTH, rides, frota)
    folga = generate_folga(TEST_MONTH)
    metas = generate_metas(TEST_MONTH, folha)

    write_workbook(
        month=TEST_MONTH,
        rides=rides,
        empresa=empresa,
        passageiro=passageiro,
        colaboradores=colaboradores,
        frota=frota,
        folha=folha,
        financeiro=financeiro,
        frota_stats=frota_stats,
        folga=folga,
        metas=metas,
        output_dir=str(tmp_dir),
    )

    xlsx_path = tmp_dir / f"VCTrans_{TEST_MONTH}.xlsx"
    assert xlsx_path.exists(), "XLSX file was not created"

    # Return both the path and the in-memory ride data for comparison
    return {"path": str(xlsx_path), "rides": rides, "financeiro": financeiro}


@pytest.fixture(scope="module")
def loaded_counts(seed_xlsx, test_conn, clean_db):
    """Run the full ETL pipeline and return row counts."""
    raw = read_workbook(seed_xlsx["path"])
    clean = transform(raw, TEST_MONTH)
    counts = load(clean, test_conn)
    return counts


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestRowCounts:
    def test_rides_count(self, loaded_counts, seed_xlsx):
        expected = len(seed_xlsx["rides"])
        assert loaded_counts["rides"] == expected, (
            f"Expected {expected} rides, got {loaded_counts['rides']}"
        )

    def test_driver_summary_count(self, loaded_counts):
        # At least 20 drivers should have worked (out of 25)
        assert loaded_counts["monthly_driver_summary"] >= 20

    def test_company_summary_count(self, loaded_counts):
        # All 8 companies should have rides
        assert loaded_counts["monthly_company_summary"] == 8

    def test_vehicle_summary_count(self, loaded_counts):
        # All 26 vehicles should have rides
        assert loaded_counts["monthly_vehicle_summary"] == 26

    def test_driver_schedule_count(self, loaded_counts):
        # All 25 drivers should have a schedule row
        assert loaded_counts["driver_schedule"] == 25

    def test_rate_history_count(self, loaded_counts):
        # All 8 companies should have rate snapshots
        assert loaded_counts["rate_history"] == 8


class TestDataIntegrity:
    def test_revenue_matches(self, test_conn, seed_xlsx):
        """
        Total revenue in monthly_company_summary must match
        the sum of all ride totals in the rides table for the same month.
        These are computed independently — if they match, the billing logic is consistent.
        """
        with test_conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(SUM(total), 0) FROM rides WHERE month = %s",
                (TEST_MONTH,)
            )
            rides_total = float(cur.fetchone()[0])

            cur.execute(
                "SELECT COALESCE(SUM(revenue_subtotal), 0) FROM monthly_company_summary WHERE month = %s",
                (TEST_MONTH,)
            )
            summary_total = float(cur.fetchone()[0])

        # Allow 1% tolerance for rounding differences
        assert abs(rides_total - summary_total) / max(rides_total, 1) < 0.01, (
            f"Revenue mismatch: rides.total sum = {rides_total:.2f}, "
            f"company_summary.revenue_subtotal sum = {summary_total:.2f}"
        )

    def test_no_null_company(self, test_conn):
        """Every ride must have a non-null company."""
        with test_conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM rides WHERE month = %s AND company IS NULL",
                (TEST_MONTH,)
            )
            null_count = cur.fetchone()[0]
        assert null_count == 0, f"{null_count} rides have null company"

    def test_no_null_driver(self, test_conn):
        """Every ride must have a non-null driver."""
        with test_conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM rides WHERE month = %s AND driver IS NULL",
                (TEST_MONTH,)
            )
            null_count = cur.fetchone()[0]
        assert null_count == 0, f"{null_count} rides have null driver"

    def test_os_numbers_unique(self, test_conn):
        """OS numbers must be unique within the month."""
        with test_conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM (
                    SELECT os_number, COUNT(*) as cnt
                    FROM rides
                    WHERE month = %s
                    GROUP BY os_number
                    HAVING COUNT(*) > 1
                ) dupes
            """, (TEST_MONTH,))
            dupes = cur.fetchone()[0]
        assert dupes == 0, f"{dupes} duplicate OS numbers found"

    def test_totals_are_positive(self, test_conn):
        """All ride totals must be > 0."""
        with test_conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM rides WHERE month = %s AND total <= 0",
                (TEST_MONTH,)
            )
            bad = cur.fetchone()[0]
        assert bad == 0, f"{bad} rides have zero or negative total"

    def test_idempotency(self, seed_xlsx, test_conn):
        """
        Running the ETL twice on the same file should produce the same row counts
        (upsert must not duplicate rows).
        """
        raw = read_workbook(seed_xlsx["path"])
        clean = transform(raw, TEST_MONTH)
        counts_second_run = load(clean, test_conn)

        with test_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM rides WHERE month = %s", (TEST_MONTH,))
            rides_in_db = cur.fetchone()[0]

        assert rides_in_db == counts_second_run["rides"], (
            "Second ETL run changed the row count — upsert is not idempotent"
        )
