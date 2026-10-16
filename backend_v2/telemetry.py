"""Optional exporter. Standard API calls are no-ops when disabled."""
import os
from opentelemetry import trace, metrics


def configure():
    if os.environ.get('OTEL_ENABLED')!='true':return
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
    resource=Resource.create({'service.name':'dealer-desk','service.version':'2.0.0'})
    provider=TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    metrics.set_meter_provider(MeterProvider(resource=resource,metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter())]))
