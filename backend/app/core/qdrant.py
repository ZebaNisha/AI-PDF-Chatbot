from qdrant_client import AsyncQdrantClient, models
import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

qdrant_client = AsyncQdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
    check_compatibility=False,
)


async def check_connection() -> bool:
    """
    Health check for Qdrant database with timeout.
    """
    try:
        import asyncio
        await asyncio.wait_for(qdrant_client.get_collections(), timeout=3.0)
        return True
    except Exception as e:
        logger.error("qdrant_connection_failed", error=str(e))
        return False


async def init_qdrant():
    """
    Initialize Qdrant collection with deep validation.
    Checks vector dimension, metric, and recreates if mismatched.
    """
    collection_name = settings.QDRANT_COLLECTION
    expected_dimension = settings.VECTOR_DIMENSION
    expected_distance = models.Distance.COSINE

    try:
        collections_response = await qdrant_client.get_collections()
        exists = any(
            c.name == collection_name for c in collections_response.collections
        )

        if exists:
            # Deep validation
            collection_info = await qdrant_client.get_collection(collection_name)
            v_params = collection_info.config.params.vectors

            # Handle both named and unnamed vector configurations
            if isinstance(v_params, dict) and "" in v_params:
                vp = v_params[""]
            else:
                vp = v_params

            dimension_mismatch = hasattr(vp, "size") and vp.size != expected_dimension
            distance_mismatch = (
                hasattr(vp, "distance") and vp.distance != expected_distance
            )

            if dimension_mismatch or distance_mismatch:
                logger.warning(
                    "qdrant_collection_mismatch_detected",
                    expected_dim=expected_dimension,
                    actual_dim=getattr(vp, "size", "unknown"),
                    expected_dist=expected_distance,
                    actual_dist=getattr(vp, "distance", "unknown"),
                    action="recreating_collection",
                )
                await qdrant_client.delete_collection(collection_name)
                exists = False  # Force creation below

        if not exists:
            # Create collection
            await qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=expected_dimension, distance=expected_distance
                ),
            )
            logger.info(
                "qdrant_collection_created",
                collection=collection_name,
                dimension=expected_dimension,
            )

            # 4. Create Payload Indexes for security and performance
            await qdrant_client.create_payload_index(
                collection_name=collection_name,
                field_name="user_id",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
            await qdrant_client.create_payload_index(
                collection_name=collection_name,
                field_name="document_id",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
            logger.info("qdrant_payload_indexes_created")
        else:
            logger.info("qdrant_collection_validated", collection=collection_name)
            # Ensure indexes exist even on existing collections
            try:
                await qdrant_client.create_payload_index(
                    collection_name=collection_name,
                    field_name="user_id",
                    field_schema=models.PayloadSchemaType.KEYWORD,
                )
                await qdrant_client.create_payload_index(
                    collection_name=collection_name,
                    field_name="document_id",
                    field_schema=models.PayloadSchemaType.KEYWORD,
                )
            except Exception:
                # Indexes might already exist, which is fine
                pass

    except Exception as e:
        logger.error("qdrant_init_failed", error=str(e))
        raise
