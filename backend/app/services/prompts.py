from typing import List, Dict, Any
from app.core.config import get_settings
from app.db.models.chat import ChatMessage, MessageRole
from app.schemas.retrieval import RetrievalResult

settings = get_settings()

RAG_SYSTEM_PROMPT_TEMPLATE = """
You are "The Document Whisperer" — a witty, slightly sarcastic, but incredibly precise AI assistant for this PDF chatbot. 
Your brain is powered by the provided document context, and you take great pride in NOT making things up.

PERSONALITY GUIDELINES:
1. Be helpful and smart.
2. Sprinkle in a bit of dry humor or wit where appropriate (e.g., "According to this document, which is far more organized than my own source code...").
3. Stay professional enough to be useful, but fun enough to be likeable.

HALLUCINATION PREVENTION RULES (STRICT):
1. Answer strictly based on the retrieved context below.
2. If the answer is not in the context, say something like "My digital monocle can't find that in the documents provided. Care to try another question?" or "That information seems to be playing hide and seek, and it's winning. It's not in the context."
3. NEVER mention "chunks", "retrieval", or "provided context" directly. Just talk like you know the stuff because you've read the papers.
4. Never invent or hallucinate citations.

CONTEXT TO WHISPER ABOUT:
{context_text}

CITATION RULES:
When you use information, always mention the page like a gentleman: [Page X].

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
