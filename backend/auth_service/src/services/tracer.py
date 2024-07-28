from opentelemetry import trace


def get_tracer_service() -> trace.Tracer:
    return trace.get_tracer(__name__)
