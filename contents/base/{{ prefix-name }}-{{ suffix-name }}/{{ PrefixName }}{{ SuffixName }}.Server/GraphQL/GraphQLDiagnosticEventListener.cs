using HotChocolate.Diagnostics;
using HotChocolate.Execution;
using HotChocolate.Execution.Instrumentation;
using Microsoft.Extensions.Logging;
using {{ PrefixName }}{{ SuffixName }}.Server.Services;
using System.Diagnostics;

namespace {{ PrefixName }}{{ SuffixName }}.Server.GraphQL;

public class GraphQLDiagnosticEventListener : DiagnosticEventListener
{
    private readonly ILogger<GraphQLDiagnosticEventListener> _logger;
    private readonly MetricsService _metricsService;

    public GraphQLDiagnosticEventListener(
        ILogger<GraphQLDiagnosticEventListener> logger,
        MetricsService metricsService)
    {
        _logger = logger;
        _metricsService = metricsService;
    }

    public override IDisposable ExecuteRequest(IRequestContext context)
    {
        var stopwatch = Stopwatch.StartNew();
        var operationName = context.Request.OperationName ?? "Unknown";

        return new RequestScope(_logger, _metricsService, operationName, stopwatch);
    }

    private class RequestScope : IDisposable
    {
        private readonly ILogger<GraphQLDiagnosticEventListener> _logger;
        private readonly MetricsService _metricsService;
        private readonly string _operationName;
        private readonly Stopwatch _stopwatch;

        public RequestScope(
            ILogger<GraphQLDiagnosticEventListener> logger,
            MetricsService metricsService,
            string operationName,
            Stopwatch stopwatch)
        {
            _logger = logger;
            _metricsService = metricsService;
            _operationName = operationName;
            _stopwatch = stopwatch;
        }

        public void Dispose()
        {
            _stopwatch.Stop();

            // Record metrics
            _metricsService.RecordRequest(_operationName, "success", _stopwatch.Elapsed.TotalSeconds);

            _logger.LogInformation(
                "GraphQL request {OperationName} completed in {ElapsedMilliseconds}ms",
                _operationName,
                _stopwatch.ElapsedMilliseconds);
        }
    }

    public override void RequestError(IRequestContext context, Exception exception)
    {
        var operationName = context.Request.OperationName ?? "Unknown";

        _metricsService.RecordError(operationName, exception.GetType().Name);

        _logger.LogError(exception,
            "GraphQL request error in operation {OperationName}",
            operationName);
    }

    public override void ValidationErrors(IRequestContext context, IReadOnlyList<IError> errors)
    {
        var operationName = context.Request.OperationName ?? "Unknown";

        foreach (var error in errors)
        {
            _metricsService.RecordValidationError(error.Code ?? "Unknown");
        }

        _logger.LogWarning(
            "GraphQL validation errors in operation {OperationName}: {ErrorCount} errors",
            operationName,
            errors.Count);
    }
}