using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Xunit;
using Xunit.Abstractions;

namespace {{ PrefixName }}{{ SuffixName }}.IntegrationTests;

[Collection("ApplicationCollection")]
public class MinimalGraphQLTest
{
    private readonly ApplicationFixture _fixture;
    private readonly ITestOutputHelper _output;

    public MinimalGraphQLTest(ApplicationFixture fixture, ITestOutputHelper output)
    {
        _fixture = fixture;
        _output = output;
    }

    [Fact]
    public async Task Test_GraphQL_Introspection()
    {
        using var client = new HttpClient();
        var url = $"http://localhost:5041/graphql";

        var query = @"{
            ""query"": ""{ __schema { queryType { name } } }""
        }";

        var content = new StringContent(query, Encoding.UTF8, "application/json");
        var response = await client.PostAsync(url, content);

        _output.WriteLine($"Status: {response.StatusCode}");
        var responseBody = await response.Content.ReadAsStringAsync();
        _output.WriteLine($"Response: {responseBody}");

        Assert.True(response.IsSuccessStatusCode, $"Expected success status, got {response.StatusCode}. Response: {responseBody}");
    }

    [Fact]
    public async Task Test_Health_Endpoint()
    {
        using var client = new HttpClient();
        var response = await client.GetAsync("http://localhost:5041/health");

        _output.WriteLine($"Health Status: {response.StatusCode}");
        var responseBody = await response.Content.ReadAsStringAsync();
        _output.WriteLine($"Health Response: {responseBody}");

        Assert.True(response.IsSuccessStatusCode);
    }

    [Fact]
    public async Task Test_Simple_Query()
    {
        using var client = new HttpClient();
        var url = $"http://localhost:5041/graphql";

        var query = @"{
            ""query"": ""{ {{ prefixName }}s(pageSize: 5) { items { id name } } }""
        }";

        var content = new StringContent(query, Encoding.UTF8, "application/json");
        var response = await client.PostAsync(url, content);

        _output.WriteLine($"Status: {response.StatusCode}");
        var responseBody = await response.Content.ReadAsStringAsync();
        _output.WriteLine($"Response: {responseBody}");

        // Don't assert success, just want to see the error
    }

    [Fact]
    public async Task Test_Delete_NonExistent()
    {
        using var client = new HttpClient();
        var url = $"http://localhost:5041/graphql";
        var nonExistentId = Guid.NewGuid().ToString();

        var query = $@"{{
            ""query"": ""mutation {{ delete{{ PrefixName }}(id: \""{nonExistentId}\"") {{'{'}}{ success message }} }}""
        }}";

        var content = new StringContent(query, Encoding.UTF8, "application/json");
        var response = await client.PostAsync(url, content);

        _output.WriteLine($"Status: {response.StatusCode}");
        var responseBody = await response.Content.ReadAsStringAsync();
        _output.WriteLine($"Response: {responseBody}");
    }
}