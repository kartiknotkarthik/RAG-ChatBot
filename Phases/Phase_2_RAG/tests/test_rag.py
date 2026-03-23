import pytest
import os
import sys
from unittest.mock import MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from Phases.Phase_2_RAG.src.database.vector_store import VectorStore
from Phases.Phase_2_RAG.src.chatbot.rag_engine import RAGEngine

@pytest.fixture
def mock_vs(tmp_path):
    # Use a temporary directory for ChromaDB if we wanted true file isolation
    # But for unit tests, we'll mock the client/collection if possible
    vs = VectorStore(persist_directory=str(tmp_path / "test_db"))
    return vs

def test_vector_store_add_and_query(mock_vs):
    # Test adding a fund
    fund_text = "Fund Name: HDFC Growth\nNAV: 100"
    metadata = {"name": "HDFC", "url": "http://example.com"}
    mock_vs.add_fund_data("fund_1", fund_text, metadata)
    
    # Test retrieval
    fund_res, reg_res = mock_vs.query("HDFC")
    assert "HDFC" in fund_res['documents'][0][0]
    assert fund_res['metadatas'][0][0]['url'] == "http://example.com"

def test_rag_guardrails():
    # We don't need a real LLM for guardrail logic check
    os.environ["OPENAI_API_KEY"] = "mock_key"
    engine = RAGEngine()
    
    # Test Advice Detection
    query = "Should I invest my 1 lakh in SBI Gold?"
    response = engine.handle_query(query)
    assert "I apologize, but I only provide factual data" in response
    assert "consult a SEBI-registered advisor" in response

def test_rag_pii_refusal():
    # Test if the bot refuses to answer questions about personal info
    os.environ["GROQ_API_KEY"] = "mock_key"
    engine = RAGEngine()
    
    query = "What is the home address of the fund manager?"
    response = engine.handle_query(query)
    assert "personal information is out of my scope" in response.lower()

def test_rag_factual_query_handling(mocker):
    # Mocking the VectorStore and LLM to test factual pipeline
    os.environ["GROQ_API_KEY"] = "mock_key"
    mock_vs = mocker.patch("Phases.Phase_2_RAG.src.chatbot.rag_engine.VectorStore")
    mock_llm = mocker.patch("Phases.Phase_2_RAG.src.chatbot.rag_engine.ChatGroq")
    
    # Create fake retrieval results
    mock_vs.return_value.query.return_value = (
        {'documents': [['The expense ratio is 0.88%']], 'metadatas': [[{'url': 'http://hdfc.com'}]]},
        {'documents': [[]]} # No reg results
    )
    
    # Create fake LLM response
    mock_response = MagicMock()
    mock_response.content = "According to records, the expense ratio is 0.88%."
    mock_llm.return_value.invoke.return_value = mock_response
    
    engine = RAGEngine()
    result = engine.handle_query("What is HDFC expense ratio?")
    
    assert "0.88%" in result
    assert "Source: http://hdfc.com" in result
    assert "No investment advice" in result

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__]))
