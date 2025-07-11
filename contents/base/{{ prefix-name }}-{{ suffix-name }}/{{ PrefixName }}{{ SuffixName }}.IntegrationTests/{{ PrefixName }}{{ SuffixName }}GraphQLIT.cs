using {{ PrefixName }}{{ SuffixName }}.API.Schema;
using {{ PrefixName }}{{ SuffixName }}.Client;
using Xunit.Abstractions;

namespace {{ PrefixName }}{{ SuffixName }}.IntegrationTests;

[Collection("ApplicationCollection")]
public class {{ PrefixName }}{{ SuffixName }}GraphQLIT(ITestOutputHelper testOutputHelper, ApplicationFixture applicationFixture)
{
    private readonly ApplicationFixture _applicationFixture = applicationFixture;
    private readonly {{ PrefixName }}{{ SuffixName }}Client _client = applicationFixture.GetClient();

    [Fact]
    public async Task Test_Create{{ PrefixName }}()
    {
        // Arrange
        var input = new Create{{ PrefixName }}Input { Name = Guid.NewGuid().ToString() };

        // Act
        var response = await _client.Create{{ PrefixName }}(input);

        // Assert
        Assert.NotNull(response);
        Assert.NotNull(response.{{ PrefixName }});
        Assert.NotNull(response.{{ PrefixName }}.Id);
        Assert.Equal(input.Name, response.{{ PrefixName }}.Name);
    }

    [Fact]
    public async Task Test_Get{{ PrefixName }}s()
    {
        testOutputHelper.WriteLine("Test_Get{{ PrefixName }}s");

        // Arrange
        var beforeResponse = await _client.Get{{ PrefixName }}s("1", 10);
        var beforeTotal = beforeResponse.TotalCount;

        // Create a new item
        var createInput = new Create{{ PrefixName }}Input { Name = Guid.NewGuid().ToString() };
        await _client.Create{{ PrefixName }}(createInput);

        // Act
        var response = await _client.Get{{ PrefixName }}s("1", 10);

        // Assert
        Assert.NotNull(response);
        Assert.Equal(beforeTotal + 1, response.TotalCount);
        Assert.NotNull(response.Items);
        Assert.NotEmpty(response.Items);
    }

    [Fact]
    public async Task Test_Get{{ PrefixName }}()
    {
        // Arrange
        var createInput = new Create{{ PrefixName }}Input { Name = Guid.NewGuid().ToString() };
        var createResponse = await _client.Create{{ PrefixName }}(createInput);
        var createdId = createResponse.{{ PrefixName }}.Id;

        // Act
        var result = await _client.Get{{ PrefixName }}(createdId!);

        // Assert
        Assert.NotNull(result);
        Assert.Equal(createdId, result.Id);
        Assert.Equal(createInput.Name, result.Name);
    }

    [Fact]
    public async Task Test_Update{{ PrefixName }}()
    {
        // Arrange
        var createInput = new Create{{ PrefixName }}Input { Name = Guid.NewGuid().ToString() };
        var createResponse = await _client.Create{{ PrefixName }}(createInput);
        var createdId = createResponse.{{ PrefixName }}.Id;

        var updateInput = new Update{{ PrefixName }}Input
        {
            Id = createdId!,
            Name = "Updated Name"
        };

        // Act
        var response = await _client.Update{{ PrefixName }}(updateInput);

        // Assert
        Assert.NotNull(response);
        Assert.NotNull(response.{{ PrefixName }});
        Assert.Equal(createdId, response.{{ PrefixName }}.Id);
        Assert.Equal("Updated Name", response.{{ PrefixName }}.Name);
    }

    [Fact]
    public async Task Test_Delete{{ PrefixName }}()
    {
        // Arrange
        var createInput = new Create{{ PrefixName }}Input { Name = Guid.NewGuid().ToString() };
        var createResponse = await _client.Create{{ PrefixName }}(createInput);
        var createdId = createResponse.{{ PrefixName }}.Id;

        // Act
        var response = await _client.Delete{{ PrefixName }}(createdId!);

        // Assert
        Assert.NotNull(response);
        Assert.True(response.Success);
        Assert.NotNull(response.Message);

        // Verify deletion
        var getResult = await _client.Get{{ PrefixName }}(createdId!);
        Assert.Null(getResult);
    }

    [Fact]
    public async Task Test_Delete{{ PrefixName }}_NotFound()
    {
        // Arrange
        var nonExistentId = Guid.NewGuid().ToString();

        // Act & Assert
        // HotChocolate returns HTTP 500 for entity not found errors, causing GraphQLHttpRequestException
        var exception = await Assert.ThrowsAsync<GraphQL.Client.Http.GraphQLHttpRequestException>(async () =>
        {
            await _client.Delete{{ PrefixName }}(nonExistentId);
        });

        // The exception message should indicate an internal server error
        Assert.Contains("InternalServerError", exception.Message);
    }

    [Fact]
    public async Task Test_Pagination()
    {
        // Arrange - Create multiple items
        var itemsToCreate = 5;
        for (int i = 0; i < itemsToCreate; i++)
        {
            var input = new Create{{ PrefixName }}Input { Name = $"Test Item {i} - {Guid.NewGuid()}" };
            await _client.Create{{ PrefixName }}(input);
        }

        // Act - Get first page
        var firstPage = await _client.Get{{ PrefixName }}s("1", 2);

        // Assert
        Assert.NotNull(firstPage);
        Assert.Equal(2, firstPage.Items.Count());
        Assert.NotNull(firstPage.PageInfo);
        Assert.True(firstPage.PageInfo.HasNextPage);
        Assert.False(firstPage.PageInfo.HasPreviousPage);

        // Act - Get next page
        var secondPage = await _client.Get{{ PrefixName }}s(firstPage.PageInfo.NextPage, 2);

        // Assert
        Assert.NotNull(secondPage);
        Assert.True(secondPage.Items.Any());
        Assert.NotNull(secondPage.PageInfo);
        Assert.True(secondPage.PageInfo.HasPreviousPage);
    }
}