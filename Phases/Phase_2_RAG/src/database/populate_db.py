from src.database.vector_store import VectorStore
import json
import os

def populate():
    vs = VectorStore()
    
    # 1. Add Funds
    master_file = 'data/processed/fund_master.json'
    if os.path.exists(master_file):
        with open(master_file, 'r', encoding='utf-8') as f:
            funds = json.load(f)
        
        for fund in funds:
            # Flatten fund data into a searchable string
            txt = f"Fund Name: {fund['fund_name']}\n"
            txt += f"AMC: {fund['amc_name']}\n"
            txt += f"Category: {', '.join(fund['categories'])}\n"
            txt += f"Strategy: {fund.get('investment_strategy', '')}\n"
            txt += f"Managers: {', '.join([m['name'] for m in fund.get('fund_managers', [])])}\n"
            txt += f"NAV: {fund['nav']}\n"
            txt += f"AUM: {fund['fund_size']}\n"
            txt += f"Expense Ratio: {fund['expense_ratio']}\n"
            txt += f"Benchmark: {fund.get('benchmark_index', '')}\n"
            
            # Metadata for citations
            meta = {
                "name": fund['fund_name'],
                "url": fund['citation_url'],
                "type": "fund_detail"
            }
            
            vs.add_fund_data(fund['fund_name'], txt, meta)
            print(f"Indexed fund: {fund['fund_name']}")

    # 2. Add Regulations
    reg_file = 'data/processed/pdfs/1719488538007_chunks.json'
    if os.path.exists(reg_file):
        with open(reg_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        vs.add_regulations(chunks)
        print(f"Indexed {len(chunks)} regulatory chunks.")

if __name__ == "__main__":
    populate()
