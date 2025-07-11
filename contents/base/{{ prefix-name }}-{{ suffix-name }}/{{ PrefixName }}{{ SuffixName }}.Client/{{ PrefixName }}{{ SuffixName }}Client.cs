using GraphQL;
using GraphQL.Client.Http;
using GraphQL.Client.Serializer.SystemTextJson;
using {{ PrefixName }}{{ SuffixName }}.API;
using {{ PrefixName }}{{ SuffixName }}.API.Schema;
using System.Net.Http.Headers;

namespace {{ PrefixName }}{{ SuffixName }}.Client;

public class {{ PrefixName }}{{ SuffixName }}Client : I{{ PrefixName }}{{ SuffixName }}, IDisposable
{
    private readonly GraphQLHttpClient _graphQLClient;
    private readonly bool _ownsHttpClient;

    private {{ PrefixName }}{{ SuffixName }}Client(GraphQLHttpClient graphQLClient, bool ownsHttpClient = true)
    {
        _graphQLClient = graphQLClient;
        _ownsHttpClient = ownsHttpClient;
    }

    public static {{ PrefixName }}{{ SuffixName }}Client Of(string endpoint, string? authToken = null)
    {
        var httpClient = new HttpClient();
        if (!string.IsNullOrEmpty(authToken))
        {
            httpClient.DefaultRequestHeaders.Authorization =
                new AuthenticationHeaderValue("Bearer", authToken);
        }

        var graphQLClient = new GraphQLHttpClient(endpoint, new SystemTextJsonSerializer(), httpClient);
        return new {{ PrefixName }}{{ SuffixName }}Client(graphQLClient);
    }

    public static {{ PrefixName }}{{ SuffixName }}Client Of(HttpClient httpClient, string endpoint)
    {
        var graphQLClient = new GraphQLHttpClient(endpoint, new SystemTextJsonSerializer(), httpClient);
        return new {{ PrefixName }}{{ SuffixName }}Client(graphQLClient, ownsHttpClient: false);
    }

    public async Task<Create{{ PrefixName }}Response> Create{{ PrefixName }}(Create{{ PrefixName }}Input input)
    {
        var mutation = new GraphQLRequest
        {
            Query = @"
                mutation Create{{ PrefixName }}($input: Create{{ PrefixName }}Input!) {
                    create{{ PrefixName }}(input: $input) {
                        {{ prefixName }} {
                            id
                            name
                        }
                    }
                }",
            Variables = new { input }
        };

        var response = await _graphQLClient.SendQueryAsync<Create{{ PrefixName }}Data>(mutation);

        if (response.Errors?.Any() == true)
        {
            throw new GraphQLException($"GraphQL errors: {string.Join(", ", response.Errors.Select(e => e.Message))}");
        }

        return response.Data.Create{{ PrefixName }};
    }

    public async Task<{{ PrefixName }}Connection> Get{{ PrefixName }}s(string? startPage, int? pageSize)
    {
        var query = new GraphQLRequest
        {
            Query = @"
                query Get{{ PrefixName }}s($startPage: String, $pageSize: Int) {
                    {{ prefixName }}s(startPage: $startPage, pageSize: $pageSize) {
                        items {
                            id
                            name
                        }
                        pageInfo {
                            hasNextPage
                            hasPreviousPage
                            startPage
                            nextPage
                            previousPage
                        }
                        totalCount
                    }
                }",
            Variables = new { startPage, pageSize }
        };

        var response = await _graphQLClient.SendQueryAsync<Get{{ PrefixName }}sData>(query);

        if (response.Errors?.Any() == true)
        {
            throw new GraphQLException($"GraphQL errors: {string.Join(", ", response.Errors.Select(e => e.Message))}");
        }

        return response.Data.{{ PrefixName }}s;
    }

    public async Task<{{ PrefixName }}Dto?> Get{{ PrefixName }}(string id)
    {
        var query = new GraphQLRequest
        {
            Query = @"
                query Get{{ PrefixName }}($id: String!) {
                    {{ prefixName }}(id: $id) {
                        id
                        name
                    }
                }",
            Variables = new { id }
        };

        var response = await _graphQLClient.SendQueryAsync<Get{{ PrefixName }}Data>(query);

        if (response.Errors?.Any() == true)
        {
            throw new GraphQLException($"GraphQL errors: {string.Join(", ", response.Errors.Select(e => e.Message))}");
        }

        return response.Data.{{ PrefixName }};
    }

    public async Task<Update{{ PrefixName }}Response> Update{{ PrefixName }}(Update{{ PrefixName }}Input input)
    {
        var mutation = new GraphQLRequest
        {
            Query = @"
                mutation Update{{ PrefixName }}($input: Update{{ PrefixName }}Input!) {
                    update{{ PrefixName }}(input: $input) {
                        {{ prefixName }} {
                            id
                            name
                        }
                    }
                }",
            Variables = new { input }
        };

        var response = await _graphQLClient.SendQueryAsync<Update{{ PrefixName }}Data>(mutation);

        if (response.Errors?.Any() == true)
        {
            throw new GraphQLException($"GraphQL errors: {string.Join(", ", response.Errors.Select(e => e.Message))}");
        }

        return response.Data.Update{{ PrefixName }};
    }

    public async Task<Delete{{ PrefixName }}Response> Delete{{ PrefixName }}(string id)
    {
        var mutation = new GraphQLRequest
        {
            Query = @"
                mutation Delete{{ PrefixName }}($id: String!) {
                    delete{{ PrefixName }}(id: $id) {
                        success
                        message
                    }
                }",
            Variables = new { id }
        };

        var response = await _graphQLClient.SendQueryAsync<Delete{{ PrefixName }}Data>(mutation);

        if (response.Errors?.Any() == true)
        {
            throw new GraphQLException($"GraphQL errors: {string.Join(", ", response.Errors.Select(e => e.Message))}");
        }

        return response.Data.Delete{{ PrefixName }};
    }

    public void Dispose()
    {
        if (_ownsHttpClient)
        {
            _graphQLClient?.Dispose();
        }
    }

    // Response data classes for deserialization
    private class Create{{ PrefixName }}Data
    {
        public Create{{ PrefixName }}Response Create{{ PrefixName }} { get; set; } = null!;
    }

    private class Get{{ PrefixName }}sData
    {
        public {{ PrefixName }}Connection {{ PrefixName }}s { get; set; } = null!;
    }

    private class Get{{ PrefixName }}Data
    {
        public {{ PrefixName }}Dto? {{ PrefixName }} { get; set; }
    }

    private class Update{{ PrefixName }}Data
    {
        public Update{{ PrefixName }}Response Update{{ PrefixName }} { get; set; } = null!;
    }

    private class Delete{{ PrefixName }}Data
    {
        public Delete{{ PrefixName }}Response Delete{{ PrefixName }} { get; set; } = null!;
    }

    public class GraphQLException : Exception
    {
        public GraphQLException(string message) : base(message) { }
    }
}