import chromadb
from chromadb.utils import embedding_functions
import os
import json

class VectorStore:
    def __init__(self, persist_directory=None):
        # Calculate absolute base directory of project
        # vector_store.py is in Phases/Phase_2_RAG/src/database/
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
        
        if persist_directory is None:
            persist_directory = os.path.join(self.base_dir, "data/database")
            
        try:
            self.client = chromadb.PersistentClient(path=persist_directory)
            self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
            
            self.fund_collection = self.client.get_or_create_collection(
                name="mutual_funds",
                embedding_function=self.embedding_fn
            )
            self.reg_collection = self.client.get_or_create_collection(
                name="regulations",
                embedding_function=self.embedding_fn
            )
        except Exception as e:
            print(f"VectorStore Init Error: {e}. Moving to Resilient mode.")
            self.client = None
            self.fund_collection = None
            self.reg_collection = None

    def add_fund_data(self, fund_id, text, metadata):
        if self.fund_collection:
            self.fund_collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[fund_id]
            )

    def add_regulations(self, chunks):
        if self.reg_collection:
            ids = [f"reg_{i}" for i in range(len(chunks))]
            self.reg_collection.add(
                documents=chunks,
                ids=ids
            )

    def query(self, query_text, n_results=3):
        try:
            # If collections are None (Resilient mode), jump to fallback
            if not self.fund_collection or not self.reg_collection:
                return self._keyword_fallback_search(query_text, n_results)

            fund_results = self.fund_collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            reg_results = self.reg_collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            # If DB is initialized but empty (common on first run or corrupt env), use fallback
            if not fund_results['documents'][0] and not reg_results['documents'][0]:
                return self._keyword_fallback_search(query_text, n_results)
                
            return fund_results, reg_results
        except Exception as e:
            print(f"ChromaDB Query Error: {e}. Switching to Keyword Fallback Search.")
            return self._keyword_fallback_search(query_text, n_results)

    def _keyword_fallback_search(self, query_text, n_results=3):
        # Fallback for environments where ONNX/Vector embeddings fail (like Python 3.14)
        import json
        fund_file = os.path.join(self.base_dir, 'data/processed/fund_master.json')
        reg_file = os.path.join(self.base_dir, 'data/processed/pdfs/1719488538007_chunks.json')
        
        fund_data = []
        if os.path.exists(fund_file):
            with open(fund_file, 'r', encoding='utf-8') as f:
                fund_data = json.load(f)
        
        reg_data = []
        if os.path.exists(reg_file):
            with open(reg_file, 'r', encoding='utf-8') as f:
                reg_data = json.load(f)
                
        q = query_text.lower()
        stopwords = {"what", "is", "the", "fund", "mutual", "to", "for", "in", "of", "and", "cap", "ratio", "expense"}
        words = [w for w in q.split() if w not in stopwords and len(w) > 3]
        
        # Search & Rank Funds
        fund_scored_matches = []
        for fund in fund_data:
            fund_str = json.dumps(fund).lower()
            score = 0
            if q in fund_str: score += 10 # Direct phrase match
            for word in words:
                if word in fund_str: score += 1
            
            if score > 0:
                fund_scored_matches.append((score, fund))
        
        # Sort by score descending
        fund_scored_matches.sort(key=lambda x: x[0], reverse=True)
        
        f_results = {"documents": [[]], "metadatas": [[]]}
        for _, m in fund_scored_matches[:n_results]:
            # Building a concise, query-relevant summary
            name = m.get('fund_name', 'Unknown Fund')
            summary_parts = [f"Fund: {name}"]
            
            # Comprehensive filtering logic for the new requested schema
            q_lower = q.lower()
            
            # Helper for structured point-wise data
            def get_point(label, value):
                clean_label = label.replace("*", "")
                return f"• {clean_label}: {value}"

            if any(k in q_lower for k in ["nav", "price", "current", "latest"]):
                summary_parts.append(get_point("NAV", m.get('nav', 'N/A')))
            
            if any(k in q_lower for k in ["launch", "inception", "history", "old"]):
                summary_parts.append(get_point("Launch Date", m.get('launch_date', 'N/A')))
                summary_parts.append(get_point("Launch NAV", m.get('nav_at_launch', 'N/A')))
            
            if any(k in q_lower for k in ["expense", "cost", "ratio", "charge", "stamp", "duty"]):
                summary_parts.append(get_point("Expense Ratio", m.get('expense_ratio', 'N/A')))
                summary_parts.append(get_point("Stamp Duty", m.get('stamp_duty', '0.005%')))
                
            if any(k in q_lower for k in ["exit", "load", "redemption", "timeline"]):
                summary_parts.append(get_point("Exit Load", m.get('exit_load', 'N/A')))
                summary_parts.append(get_point("Redemption Timeline", m.get('redemption_timeline', 'N/A')))
                
            if any(k in q_lower for k in ["tax", "stcg", "ltcg", "rules"]):
                summary_parts.append(get_point("Taxation", m.get('taxation', 'N/A')))

            if any(k in q_lower for k in ["return", "performance", "growth", "yield"]):
                perf = m.get('performance', {})
                ret_str = ", ".join([f"{k}: {v}" for k, v in perf.items()])
                summary_parts.append(get_point("Performance", ret_str))
                
            if any(k in q_lower for k in ["size", "aum", "asset", "structure"]):
                summary_parts.append(get_point("Fund Size (AUM)", m.get('fund_size', 'N/A')))
                
            if any(k in q_lower for k in ["manager", "who managed", "experience"]):
                managers_list = [f"{man.get('name')} (Tenure: {man.get('tenure', 'N/A')})" for man in m.get('fund_managers', [])]
                summary_parts.append(get_point("Managers", ', '.join(managers_list)))
                
            if any(k in q_lower for k in ["sip", "lumpsum", "minimum", "min"]):
                summary_parts.append(get_point("Min SIP", m.get('min_sip', 'N/A')))
                summary_parts.append(get_point("Min Lumpsum", m.get('min_lumpsum', 'N/A')))

            if any(k in q_lower for k in ["strategy", "objective", "style", "bench", "index"]):
                summary_parts.append(get_point("Benchmank", m.get('benchmark_index', 'N/A')))
                summary_parts.append(get_point("Objective", m.get('investment_strategy', m.get('investment_objective', 'N/A'))))

            # Default if no specific metric was hit (Minimal summary)
            if len(summary_parts) == 1:
                summary_parts.append(get_point("NAV", m.get('nav', 'N/A')))
                summary_parts.append(get_point("Expense Ratio", m.get('expense_ratio', 'N/A')))
                summary_parts.append(get_point("Risk", m.get('risk_level', 'N/A')))
            
            summary = "\n".join(summary_parts)
            f_results["documents"][0].append(summary)
            f_results["metadatas"][0].append({"url": m.get("citation_url", "https://groww.in")})

        # Search & Rank Regulations
        reg_scored_matches = []
        for chunk in reg_data:
            score = 0
            if q in chunk.lower(): score += 5
            for word in words:
                if word in chunk.lower(): score += 1
            if score > 0:
                reg_scored_matches.append((score, chunk))
        
        reg_scored_matches.sort(key=lambda x: x[0], reverse=True)
        
        r_results = {"documents": [[]], "metadatas": [[]]}
        for _, m in reg_scored_matches[:n_results]:
            r_results["documents"][0].append(m)
            r_results["metadatas"][0].append({"url": "SEBI Master Circular 2024"})
            
        return f_results, r_results

if __name__ == "__main__":
    # Test
    vs = VectorStore()
    print("Vector Store initialized.")
