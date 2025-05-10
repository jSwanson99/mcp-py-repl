import os

from traceloop.sdk import Traceloop

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter


def init_otel():
    otel_service_name = os.getenv("OTEL_SERVICE_NAME", "")
    collector_url = os.getenv("COLLECTOR_URL", "")

    if otel_service_name != "" and collector_url != "":
        trace_exporter = OTLPSpanExporter(endpoint=f"{collector_url}/v1/traces")
        metric_exporter = OTLPMetricExporter(endpoint=f"{collector_url}/v1/metrics")
        log_exporter = OTLPLogExporter(endpoint=f"{collector_url}/v1/logs")

        Traceloop.init(
            app_name=otel_service_name,
            exporter=trace_exporter,
            metrics_exporter=metric_exporter,
            logging_exporter=log_exporter,
            enabled=True
        )


if __name__ == "__main__":
    init_otel()
