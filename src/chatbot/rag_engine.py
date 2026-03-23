import os
from langchain_openai import ChatOpenAI
from src.database.vector_store import VectorStore
from dotenv import load_dotenv

load_dotenv()

class RAGEngine:
    def __init__(self):
        self.vs = VectorStore()
        # Using a model that supports reasoning/factual query
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0) # Low temp for factual answers
        
        self.disclaimer = "Facts-only. No investment advice."
        self.system_prompt = f"""You are a Mutual Fund Expert Chatbot. 
Your goal is to answer factual questions about mutual funds, costs, performance, and SEBI regulations.

Rules:
1. Only answer based on the provided context. 
2. BE POLITE and decline any requests for portfolio advice, stock picks, or 'what should I invest in?'.
3. Always include one clear citation link at the end of the answer.
4. Disclaimer: {self.disclaimer}
"""

    def handle_query(self, user_query):
        # 1. Guardrail Check (Basic Keyword check)
        advice_words = ["should I invest", "buy", "sell", "portfolio advice", "best fund to"]
        if any(word in user_query.lower() for word in advice_words):
            return "I apologize, but I only provide factual data and regulatory information. I cannot offer investment advice or recommendations. Please consult a SEBI-registered advisor for portfolio decisions."

        # 2. Retrieval
        fund_res, reg_res = self.vs.query(user_query)
        
        context = ""
        citation_url = "https://www.amfiindia.com/" # Default
        
        # Extract context from results
        if fund_res['documents'] and fund_res['documents'][0]:
            context += "Fund Details:\n" + "\n".join(fund_res['documents'][0])
            citation_url = fund_res['metadatas'][0][0]['url']
            
        if reg_res['documents'] and reg_res['documents'][0]:
            context += "\nRegulatory Context:\n" + "\n".join(reg_res['documents'][0])

        # 3. Augment and Generate
        full_prompt = f"{self.system_prompt}\n\nContext:\n{context}\n\nUser Question: {user_query}\nAnswer:"
        
        try:
            response = self.llm.invoke(full_prompt)
            answer = response.content
        except Exception as e:
            answer = f"Error generating answer: {str(e)}"

        # 4. Final Formatting
        return f"{answer}\n\n**Source:** {citation_url}\n\n---\n*{self.disclaimer}*"

if __name__ == "__main__":
    engine = RAGEngine()
    print(engine.handle_query("What is the expense ratio of HDFC Large and Mid Cap Fund?"))
