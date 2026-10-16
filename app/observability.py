import logging

logger = logging.getLogger(__name__)


def configure_observability(endpoint: str | None) -> None:
    """Enable Phoenix tracing when a collector is available; never block the API."""
    if not endpoint:
        return
    try:
        from phoenix.otel import register
        from openinference.instrumentation.langchain import LangChainInstrumentor

        tracer_provider = register(project_name="intelligence-system", endpoint=endpoint)
        LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
    except Exception as error:  # local usage must remain available without Phoenix
        logger.warning("Phoenix tracing unavailable: %s", error)
