using HotChocolate;
using HotChocolate.Authorization;
using HotChocolate.Types;
using Microsoft.Extensions.Logging;
using {{ PrefixName }}{{ SuffixName }}.API.Schema;
using {{ PrefixName }}{{ SuffixName }}.Core;

namespace {{ PrefixName }}{{ SuffixName }}.Server.GraphQL;

[ExtendObjectType("Query")]
public class {{ PrefixName }}Queries
{
    private readonly ILogger<{{ PrefixName }}Queries> _logger;

    public {{ PrefixName }}Queries(ILogger<{{ PrefixName }}Queries> logger)
    {
        _logger = logger;
    }

    [Authorize(Roles = new[] { "read", "write", "admin" })]
    public async Task<{{ PrefixName }}Dto?> Get{{ PrefixName }}(
        string id,
        [Service] {{ PrefixName }}{{ SuffixName }}Core core,
        CancellationToken cancellationToken)
    {
        var startTime = DateTime.UtcNow;
        _logger.LogInformation("Get{{ PrefixName }} called with id: {Id}", id);

        try
        {
            var result = await core.Get{{ PrefixName }}(id);

            var executionTime = (DateTime.UtcNow - startTime).TotalMilliseconds;
            _logger.LogInformation("Get{{ PrefixName }} completed in {ExecutionTime}ms", executionTime);

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in Get{{ PrefixName }}");
            throw;
        }
    }

    [Authorize(Roles = new[] { "read", "write", "admin" })]
    public async Task<{{ PrefixName }}Connection> Get{{ PrefixName }}s(
        string? startPage,
        int? pageSize,
        [Service] {{ PrefixName }}{{ SuffixName }}Core core,
        CancellationToken cancellationToken)
    {
        var startTime = DateTime.UtcNow;
        _logger.LogInformation("Get{{ PrefixName }}s called with startPage: {StartPage}, pageSize: {PageSize}",
            startPage, pageSize);

        try
        {
            var result = await core.Get{{ PrefixName }}s(startPage, pageSize);

            var executionTime = (DateTime.UtcNow - startTime).TotalMilliseconds;
            _logger.LogInformation("Get{{ PrefixName }}s completed in {ExecutionTime}ms with {Count} items",
                executionTime, result.Items.Count);

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in Get{{ PrefixName }}s");
            throw;
        }
    }
}