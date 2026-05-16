from typing import List, Dict, Any
from app.core.config import get_settings
from app.db.models.chat import ChatMessage, MessageRole
from app.schemas.retrieval import RetrievalResult

settings = get_settings()

RAG_SYSTEM_PROMPT_TEMPLATE = """
You are a helpful and precise AI assistant for a PDF chatbot. 
Your task is to answer the user's question accurately using ONLY the provided document context.

HALLUCINATION PREVENTION RULES:
1. Answer strictly based on the retrieved context below.
2. If the answer is not contained within the context, state that you do not have enough information. Do NOT invent information.
3. Never mention the retrieval process or the context chunks (e.g., do not say "Based on chunk 1...").
4. Never invent or hallucinate citations that are not present.

CONTEXT:
{context_text}

CITATION INSTRUCTIONS:
When you use information from the context, always include the page numbers if available (e.g., [Page 5]).

PROMPT VERSION: {version}
"""

class PromptService:
    @staticmethod
    def build_context_text(results: List[RetrievalResult]) -> str:
        """
        Deduplicates and formats retrieved chunks into a single string for the prompt.
        """
        if not results:
            return "No relevant context found."
            
        context_parts = []
        for i, res in enumerate(results):
            part = f"--- CONTEXT BLOCK {i+1} (Source: {res.citation.document_title or 'Unknown'}, Pages: {res.citation.start_page}-{res.citation.end_page}) ---\n{res.text}"
            context_parts.append(part)
            
        return "\n\n".join(context_parts)

    @staticmethod
    def format_history(messages: List[ChatMessage]) -> List[Dict[str, str]]:
        """
        Formats database messages into a standardized chat format compatible with Groq/OpenAI.
        """
        return [{"role": msg.role, "content": msg.content} for msg in messages]

    @staticmethod
    def build_final_messages(
        query: str, 
        context_text: str, 
        history: List[ChatMessage]
    ) -> List[Dict[str, str]]:
        """
        Assembles the full prompt messages: System -> History -> User Query.
        """
        system_content = RAG_SYSTEM_PROMPT_TEMPLATE.format(
            context_text=context_text,
            version=settings.CHAT_SYSTEM_PROMPT_VERSION
        )
        
        messages = [{"role": "system", "content": system_content}]
        messages.extend(PromptService.format_history(history))
        messages.append({"role": "user", "content": query})
        
        return messages
