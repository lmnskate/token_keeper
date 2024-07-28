from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .config import jaeger_settings


def configure_tracer() -> None:
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
                agent_host_name=jaeger_settings.host,
                agent_port=jaeger_settings.http_port,
            )
        )
    )
