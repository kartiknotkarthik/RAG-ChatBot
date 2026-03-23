import os
from langchain_groq import ChatGroq
from Phases.Phase_2_RAG.src.database.vector_store import VectorStore
from dotenv import load_dotenv

load_dotenv()

class RAGEngine:
    def __init__(self):
        self.vs = VectorStore()
        # Handle Local-Only fallback if no key is present
        self.api_key = os.getenv("GROQ_API_KEY")
        self.local_mode = False
        
        if not self.api_key or "your_" in self.api_key:
            print("WARNING: No Groq API Key found. Running in LOCAL-ONLY heuristic mode.")
            self.local_mode = True
            self.llm = None
        else:
            try:
                self.llm = ChatGroq(model="llama-3.1-70b-versatile", temperature=0)
            except Exception as e:
                print(f"Error initializing Groq: {e}. Falling back to Local Mode.")
                self.local_mode = True
                self.llm = None
        
        self.disclaimer = "Facts-only. No investment advice."
        self.system_prompt = f"""You are a Mutual Fund Expert Chatbot. 
STRICT RULES:
1. ONLY answer based on the provided context. 
2. NO PERSONAL INFORMATION.
3. NO INVESTMENT ADVICE.
DISCLOSURE: {self.disclaimer}
"""

    def _highlight_query_keywords(self, text, user_query):
        import re
        q = user_query.lower()
        stopwords = {"what", "is", "the", "fund", "mutual", "to", "for", "in", "of", "and", "how", "much", "does", "get", "show", "me", "tell", "it", "this", "that", "those", "are", "name", "who"}
        # Extract meaningful keywords (length > 3, not a stopword)
        words = [w.strip("?,.!():") for w in q.split() if w.lower() not in stopwords and len(w) > 3]
        
        # Also include specific finance terms that might be short but important
        financial_terms = ["nav", "sip", "sip", "fee", "tax"]
        for term in financial_terms:
            if term in q and term not in words:
                words.append(term)

        highlighted_text = text
        # Deduplicate and sort keywords by length (longest first) to avoid partial bolding issues
        words = sorted(list(set(words)), key=len, reverse=True)
        
        for word in words:
            # Case-insensitive replacement of query keywords with <b> wrapped version
            # We ensure we don't bold something already inside a <b> tag
            pattern = re.compile(r'(?<!<b>)' + re.escape(word) + r'(?!</b>)', re.IGNORECASE)
            highlighted_text = pattern.sub(f"<b>\\g<0></b>", highlighted_text)

        return highlighted_text

    def handle_query(self, user_query):
        q = user_query.lower().strip()
        
        # 0. Greeting Check
        if q in ["hi", "hey", "hello"]:
            return "What can i do for you?"

        # 1. Scope & Privacy Guardrail Check
        pii_keywords = ["address", "phone", "email", "ssn", "aadhar", "pan"]
        advice_words = ["should i invest", "buy", "sell", "portfolio advice", "best fund to"]
        
        if any(word in q for word in pii_keywords):
            return "Local Mode: Personal information requests are out of scope."
            
        if any(word in q for word in advice_words):
            return "Local Mode: I cannot provide investment advice. Please consult a professional."

        # 2. Retrieval
        fund_res, reg_res = self.vs.query(user_query)
        
        context = ""
        citation_url = "https://www.amfiindia.com/"
        
        if fund_res['documents'] and fund_res['documents'][0]:
            context = fund_res['documents'][0][0]
            citation_url = fund_res['metadatas'][0][0]['url']
            
        if not context and reg_res['documents'] and reg_res['documents'][0]:
            context = reg_res['documents'][0][0]

        # 3. Mode Handling
        final_answer = ""
        if self.local_mode:
            if not context:
                final_answer = f"I apologize, but I couldn't find any specific facts for '{user_query}' in my local database."
            else:
                final_answer = context
        else:
            # LLM Mode
            full_context = f"Funds:\n{fund_res['documents'][0]}\n\nRegs:\n{reg_res['documents'][0]}"
            full_prompt = f"{self.system_prompt}\n\nContext:\n{full_context}\n\nUser Question: {user_query}\nAnswer:"
            try:
                response = self.llm.invoke(full_prompt)
                final_answer = response.content.replace("*", "")
            except Exception:
                final_answer = context if context else f"I apologize, but I encountered an issue and couldn't find specific facts for '{user_query}'."

        # 4. Final Formatting (Keyword Highlighting + Metadata)
        highlighted_answer = self._highlight_query_keywords(final_answer, user_query)
        
        return f"{highlighted_answer}\n\nSource: {citation_url}\n\n---\n{self.disclaimer}"

if __name__ == "__main__":
    engine = RAGEngine()
    print(engine.handle_query("What is the expense ratio of HDFC Large and Mid Cap Fund?"))
