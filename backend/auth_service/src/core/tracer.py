from asgi_correlation_id import correlation_id
from fastapi import Request
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from services.tracer import get_tracer_session


def configure_tracer(
    host: str,
    port: int
) -> None:
    tracer_provider = TracerProvider(
        resource=Resource.create(
            {
                SERVICE_NAME: 'auth'
            }
        )
    )

    trace.set_tracer_provider(tracer_provider)

    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=host,
                agent_port=port
            )
        )
    )


async def jaeger_middleware(request: Request, call_next):
    with get_tracer_session().start_as_current_span(request.url.path) as span:
        span.set_attribute(
            'http.request_id',
            str(correlation_id.get())
        )

        response = await call_next(request)
        return response
