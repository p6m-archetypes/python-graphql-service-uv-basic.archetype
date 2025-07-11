using HotChocolate;
using Microsoft.Extensions.Logging;
using {{ PrefixName }}{{ SuffixName }}.Core.Exceptions;
using System.Net;

namespace {{ PrefixName }}{{ SuffixName }}.Server.GraphQL;

public class GraphQLErrorFilter : IErrorFilter
{
    private readonly ILogger<GraphQLErrorFilter> _logger;

    public GraphQLErrorFilter(ILogger<GraphQLErrorFilter> logger)
    {
        _logger = logger;
    }

    public IError OnError(IError error)
    {
        if (error.Exception is ValidationException validationEx)
        {
            _logger.LogWarning("Validation error: {Message}", validationEx.Message);
            return error
                .WithMessage(validationEx.Message)
                .WithCode("VALIDATION_ERROR")
                .RemoveExtension("stackTrace");
        }

        if (error.Exception is EntityNotFoundException notFoundEx)
        {
            _logger.LogWarning("Not found: {Message}", notFoundEx.Message);
            return error
                .WithMessage(notFoundEx.Message)
                .WithCode("NOT_FOUND")
                .RemoveExtension("stackTrace");
        }

        if (error.Exception is UnauthorizedAccessException)
        {
            _logger.LogWarning("Unauthorized access attempt");
            return error
                .WithMessage("Unauthorized")
                .WithCode("UNAUTHORIZED")
                .RemoveExtension("stackTrace");
        }

        // Log unexpected errors
        _logger.LogError(error.Exception, "Unhandled GraphQL error");

        // In development, return more details
        var isDevelopment = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") == "Development";
        if (isDevelopment && error.Exception != null)
        {
            return error
                .WithMessage($"Internal error: {error.Exception.Message}")
                .WithCode("INTERNAL_ERROR");
        }

        // Return generic error for production
        return error
            .WithMessage("An error occurred while processing your request")
            .WithCode("INTERNAL_ERROR")
            .RemoveExtension("stackTrace");
    }
}