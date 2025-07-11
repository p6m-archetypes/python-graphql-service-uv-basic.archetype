using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using {{ PrefixName }}{{ SuffixName }}.Server;

class TestGraphQL
{
    static async Task Main(string[] args)
    {
        // Set up environment
        Environment.SetEnvironmentVariable("DISABLE_AUTH", "true");
        Environment.SetEnvironmentVariable("LOG_LEVEL", "Debug");
        Environment.SetEnvironmentVariable("ASPNETCORE_ENVIRONMENT", "Development");
        Environment.SetEnvironmentVariable("HTTP_PORT", "5045");

        var server = new {{ PrefixName }}{{ SuffixName }}Server()
            .WithEphemeral()
            .Start();

        await Task.Delay(3000); // Wait for server to start

        try
        {
            var client = new HttpClient();
            
            // Test 1: Health check
            var healthResponse = await client.GetAsync("http://localhost:5045/health");
            Console.WriteLine($"Health check: {healthResponse.StatusCode}");
            
            // Test 2: GraphQL introspection
            var introspectionQuery = @"{
                ""query"": ""{ __schema { queryType { name } } }""
            }";
            
            var content = new StringContent(introspectionQuery, Encoding.UTF8, "application/json");
            var graphqlResponse = await client.PostAsync("http://localhost:5045/graphql", content);
            
            Console.WriteLine($"GraphQL response: {graphqlResponse.StatusCode}");
            var responseBody = await graphqlResponse.Content.ReadAsStringAsync();
            Console.WriteLine($"Response body: {responseBody}");
            
            // Test 3: Try a simple query
            var simpleQuery = @"{
                ""query"": ""{ {{ prefixName }}s(pageSize: 5) { items { id name } } }""
            }";
            
            content = new StringContent(simpleQuery, Encoding.UTF8, "application/json");
            graphqlResponse = await client.PostAsync("http://localhost:5045/graphql", content);
            
            Console.WriteLine($"\nQuery response: {graphqlResponse.StatusCode}");
            responseBody = await graphqlResponse.Content.ReadAsStringAsync();
            Console.WriteLine($"Response body: {responseBody}");
        }
        finally
        {
            server.Stop();
        }
    }
}