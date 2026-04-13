"""
Entry point for the seed data generator.
Run with: python -m seed.main
Outputs 3 XLSX files into seed/output/
"""

import os
from seed.config import MONTHS, OS_NUMBER_START
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


def main():
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    # Master data is identical across all months
    empresa = generate_empresa()
    passageiro = generate_passageiro()
    colaboradores = generate_colaboradores()
    frota = generate_frota()

    print(f"Master data: {len(empresa)} companies, {len(passageiro)} passengers, "
          f"{len(colaboradores)} staff, {len(frota)} vehicles")

    os_counter = OS_NUMBER_START

    for month in MONTHS:
        print(f"\n--- {month} ---")
        rides = generate_rides(month, passageiro, os_counter)
        os_counter += len(rides)

        folha = generate_folha(month, rides)
        financeiro = generate_financeiro(month, rides)
        frota_stats = generate_frota_stats(month, rides, frota)
        folga = generate_folga(month)
        metas = generate_metas(month, folha)

        write_workbook(
            month=month,
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
            output_dir=output_dir,
        )

        # Summary stats
        total_revenue = sum(r["total"] for r in rides)
        company_counts: dict[str, int] = {}
        for r in rides:
            company_counts[r["company"]] = company_counts.get(r["company"], 0) + 1

        print(f"  Rides:   {len(rides)}")
        print(f"  Revenue: R$ {total_revenue:,.2f}")
        print(f"  By company:")
        for company, count in sorted(company_counts.items(), key=lambda x: -x[1]):
            pct = count / len(rides) * 100
            print(f"    {company}: {count} rides ({pct:.1f}%)")

    print("\nDone. Files saved to seed/output/")


if __name__ == "__main__":
    main()
