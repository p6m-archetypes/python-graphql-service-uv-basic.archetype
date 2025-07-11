using {{ PrefixName }}{{ SuffixName }}.Client;
using {{ PrefixName }}{{ SuffixName }}.Server;

namespace {{ PrefixName }}{{ SuffixName }}.IntegrationTests;

public class ApplicationFixture : IDisposable
{
    private readonly {{ PrefixName }}{{ SuffixName }}Server _server;
    private readonly {{ PrefixName }}{{ SuffixName }}Client _client;
    public ApplicationFixture()
    {
        // Disable authentication for integration tests
        Environment.SetEnvironmentVariable("DISABLE_AUTH", "true");
        // Enable debug logging
        Environment.SetEnvironmentVariable("LOG_LEVEL", "Debug");
        Environment.SetEnvironmentVariable("ASPNETCORE_ENVIRONMENT", "Development");
        Environment.SetEnvironmentVariable("CORE_LOG_LEVEL", "Debug");
        Environment.SetEnvironmentVariable("GRPC_LOG_LEVEL", "Debug");

        _server = new {{ PrefixName }}{{ SuffixName }}Server()
            .WithEphemeral()
            .WithRandomPorts()
            .Start();

        // Wait for server to be fully started
        Thread.Sleep(2000);

        var graphQLUrl = GetGraphQLUrl();
        if (string.IsNullOrEmpty(graphQLUrl))
        {
            throw new InvalidOperationException("Failed to get GraphQL server URL");
        }

        _client = {{ PrefixName }}{{ SuffixName }}Client.Of(graphQLUrl);
    }

    private string GetGraphQLUrl()
    {
        // Get the HTTP port from the server configuration
        var httpPort = _server.GetConfiguration()["HTTP_PORT"] ?? "5031";
        return $"http://localhost:{httpPort}/graphql";
    }

    public {{ PrefixName }}{{ SuffixName }}Client GetClient() => _client;
    public {{ PrefixName }}{{ SuffixName }}Server GetServer() => _server;

    public void Dispose()
    {
        _server.Stop();
    }
}

[CollectionDefinition("ApplicationCollection")]
public class ApplicationCollection : ICollectionFixture<ApplicationFixture>
{
    // This class has no code; it's just a marker for the test collection
}