using HotChocolate.Authorization;
using HotChocolate.Execution.Configuration;
using HotChocolate.Resolvers;
using Microsoft.Extensions.DependencyInjection;

namespace {{ PrefixName }}{{ SuffixName }}.Server.Authorization;

/// <summary>
/// Authorization handler that allows all requests when DISABLE_AUTH is set to true
/// </summary>
public class TestAuthorizationHandler : IAuthorizationHandler
{
    private readonly IConfiguration _configuration;

    public TestAuthorizationHandler(IConfiguration configuration)
    {
        _configuration = configuration;
    }

    public ValueTask<AuthorizeResult> AuthorizeAsync(
        IMiddlewareContext context,
        AuthorizeDirective directive,
        CancellationToken cancellationToken = default)
    {
        // If auth is disabled, allow all requests
        if (_configuration["DISABLE_AUTH"] == "true")
        {
            return new ValueTask<AuthorizeResult>(AuthorizeResult.Allowed);
        }

        // Otherwise, deny (real auth should be handled by default handler)
        return new ValueTask<AuthorizeResult>(AuthorizeResult.NotAllowed);
    }

    public ValueTask<AuthorizeResult> AuthorizeAsync(
        AuthorizationContext context,
        IReadOnlyList<AuthorizeDirective> directives,
        CancellationToken cancellationToken = default)
    {
        // If auth is disabled, allow all requests
        if (_configuration["DISABLE_AUTH"] == "true")
        {
            return new ValueTask<AuthorizeResult>(AuthorizeResult.Allowed);
        }

        // Otherwise, deny (real auth should be handled by default handler)
        return new ValueTask<AuthorizeResult>(AuthorizeResult.NotAllowed);
    }
}

/// <summary>
/// Extension methods for configuring test authorization
/// </summary>
public static class TestAuthorizationExtensions
{
    public static IRequestExecutorBuilder AddTestAuthorization(
        this IRequestExecutorBuilder builder,
        IConfiguration configuration)
    {
        if (configuration["DISABLE_AUTH"] == "true")
        {
            // Replace the default authorization handler with our test handler
            builder.Services.AddSingleton<IAuthorizationHandler, TestAuthorizationHandler>();
        }

        return builder.AddAuthorization();
    }
}