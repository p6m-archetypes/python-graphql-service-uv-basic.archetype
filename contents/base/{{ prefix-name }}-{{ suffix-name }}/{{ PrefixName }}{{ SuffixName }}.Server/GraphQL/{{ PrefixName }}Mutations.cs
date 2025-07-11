using HotChocolate;
using HotChocolate.Authorization;
using HotChocolate.Types;
using Microsoft.Extensions.Logging;
using {{ PrefixName }}{{ SuffixName }}.API.Schema;
using {{ PrefixName }}{{ SuffixName }}.Core;

namespace {{ PrefixName }}{{ SuffixName }}.Server.GraphQL;

[ExtendObjectType("Mutation")]
public class {{ PrefixName }}Mutations
{
    private readonly ILogger<{{ PrefixName }}Mutations> _logger;

    public {{ PrefixName }}Mutations(ILogger<{{ PrefixName }}Mutations> logger)
    {
        _logger = logger;
    }

    [Authorize(Roles = new[] { "write", "admin" })]
    public async Task<Create{{ PrefixName }}Response> Create{{ PrefixName }}(
        Create{{ PrefixName }}Input input,
        [Service] {{ PrefixName }}{{ SuffixName }}Core core,
        CancellationToken cancellationToken)
    {
        var startTime = DateTime.UtcNow;
        _logger.LogInformation("Create{{ PrefixName }} called with name: {Name}", input.Name);

        try
        {
            var result = await core.Create{{ PrefixName }}(input);

            var executionTime = (DateTime.UtcNow - startTime).TotalMilliseconds;
            _logger.LogInformation("Create{{ PrefixName }} completed in {ExecutionTime}ms with id: {Id}",
                executionTime, result.{{ PrefixName }}.Id);

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in Create{{ PrefixName }}");
            throw;
        }
    }

    [Authorize(Roles = new[] { "write", "admin" })]
    public async Task<Update{{ PrefixName }}Response> Update{{ PrefixName }}(
        Update{{ PrefixName }}Input input,
        [Service] {{ PrefixName }}{{ SuffixName }}Core core,
        CancellationToken cancellationToken)
    {
        var startTime = DateTime.UtcNow;
        _logger.LogInformation("Update{{ PrefixName }} called with id: {Id}, name: {Name}",
            input.Id, input.Name);

        try
        {
            var result = await core.Update{{ PrefixName }}(input);

            var executionTime = (DateTime.UtcNow - startTime).TotalMilliseconds;
            _logger.LogInformation("Update{{ PrefixName }} completed in {ExecutionTime}ms", executionTime);

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in Update{{ PrefixName }}");
            throw;
        }
    }

    [Authorize(Roles = new[] { "admin" })]
    public async Task<Delete{{ PrefixName }}Response> Delete{{ PrefixName }}(
        string id,
        [Service] {{ PrefixName }}{{ SuffixName }}Core core,
        CancellationToken cancellationToken)
    {
        var startTime = DateTime.UtcNow;
        _logger.LogInformation("Delete{{ PrefixName }} called with id: {Id}", id);

        try
        {
            var result = await core.Delete{{ PrefixName }}(id);

            var executionTime = (DateTime.UtcNow - startTime).TotalMilliseconds;
            _logger.LogInformation("Delete{{ PrefixName }} completed in {ExecutionTime}ms", executionTime);

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in Delete{{ PrefixName }}");
            throw;
        }
    }
}