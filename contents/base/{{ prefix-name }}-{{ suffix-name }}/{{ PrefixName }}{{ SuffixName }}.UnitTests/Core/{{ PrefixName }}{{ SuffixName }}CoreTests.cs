using {{ PrefixName }}{{ SuffixName }}.API;
using {{ PrefixName }}{{ SuffixName }}.API.Schema;
using {{ PrefixName }}{{ SuffixName }}.Core;
using {{ PrefixName }}{{ SuffixName }}.Core.Services;
using {{ PrefixName }}{{ SuffixName }}.Persistence.Entities;
using {{ PrefixName }}{{ SuffixName }}.Persistence.Models;
using {{ PrefixName }}{{ SuffixName }}.Persistence.Repositories;
using {{ PrefixName }}{{ SuffixName }}.UnitTests.TestBuilders;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Moq;

namespace {{ PrefixName }}{{ SuffixName }}.UnitTests.Core;

public class {{ PrefixName }}{{ SuffixName }}CoreTests
{
    private readonly Mock<I{{ PrefixName }}Repository> _mockRepository;
    private readonly Mock<IValidationService> _mockValidationService;
    private readonly Mock<ILogger<{{ PrefixName }}{{ SuffixName }}Core>> _mockLogger;
    private readonly {{ PrefixName }}{{ SuffixName }}Core _service;

    public {{ PrefixName }}{{ SuffixName }}CoreTests()
    {
        _mockRepository = new Mock<I{{ PrefixName }}Repository>();
        _mockValidationService = new Mock<IValidationService>();
        _mockLogger = new Mock<ILogger<{{ PrefixName }}{{ SuffixName }}Core>>();

        // Setup validation service to allow valid inputs by default
        _mockValidationService
            .Setup(x => x.ValidateAndParseId(It.IsAny<string>(), It.IsAny<string>()))
            .Returns<string, string>((id, field) => Guid.Parse(id));

        _service = new {{ PrefixName }}{{ SuffixName }}Core(
            _mockRepository.Object,
            _mockValidationService.Object,
            _mockLogger.Object);
    }

    [Fact]
    public async Task Create{{ PrefixName }}_ShouldReturnCreatedEntity_WhenValidRequest()
    {
        // Arrange
        var request = new Create{{ PrefixName }}Input { Name = "Test Entity" };
        var savedEntity = new {{ PrefixName }}EntityBuilder()
            .WithName(request.Name)
            .WithId(Guid.NewGuid())
            .Generate();

        _mockRepository.Setup(x => x.Save(It.IsAny<{{ PrefixName }}Entity>()))
            .Callback<{{ PrefixName }}Entity>(entity => entity.Id = savedEntity.Id);
        _mockRepository.Setup(x => x.SaveChangesAsync())
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.Create{{ PrefixName }}(request);

        // Assert
        result.Should().NotBeNull();
        result.{{ PrefixName }}.Should().NotBeNull();
        result.{{ PrefixName }}.Id.Should().Be(savedEntity.Id.ToString());
        result.{{ PrefixName }}.Name.Should().Be(savedEntity.Name);
        _mockValidationService.Verify(x => x.ValidateCreateRequest(request), Times.Once);
        _mockRepository.Verify(x => x.Save(It.IsAny<{{ PrefixName }}Entity>()), Times.Once);
        _mockRepository.Verify(x => x.SaveChangesAsync(), Times.Once);
    }

    [Fact]
    public async Task Get{{ PrefixName }}_ShouldReturnEntity_WhenEntityExists()
    {
        // Arrange
        var entityId = Guid.NewGuid();
        var entity = new {{ PrefixName }}EntityBuilder()
            .WithId(entityId)
            .WithName("Test Entity")
            .Generate();

        _mockRepository.Setup(x => x.FindByIdAsync(entityId))
            .ReturnsAsync(entity);

        // Act
        var result = await _service.Get{{ PrefixName }}(entityId.ToString());

        // Assert
        result.Should().NotBeNull();
        result!.Id.Should().Be(entity.Id.ToString());
        result.Name.Should().Be(entity.Name);
        _mockRepository.Verify(x => x.FindByIdAsync(entityId), Times.Once);
    }

    [Fact]
    public async Task Get{{ PrefixName }}_ShouldReturnNull_WhenEntityDoesNotExist()
    {
        // Arrange
        var entityId = Guid.NewGuid();
        _mockRepository.Setup(x => x.FindByIdAsync(entityId))
            .ReturnsAsync(({{ PrefixName }}Entity?)null);

        // Act
        var result = await _service.Get{{ PrefixName }}(entityId.ToString());

        // Assert
        result.Should().BeNull();
        _mockRepository.Verify(x => x.FindByIdAsync(entityId), Times.Once);
    }

    [Fact]
    public async Task Get{{ PrefixName }}s_ShouldReturnPagedResult_WithCorrectPagination()
    {
        // Arrange
        var entities = new {{ PrefixName }}EntityBuilder().Generate(5);

        _mockRepository.Setup(x => x.FindAsync(It.IsAny<PageRequest>()))
            .ReturnsAsync(new Page<{{ PrefixName }}Entity>
            {
                Items = entities,
                TotalElements = 10
            });

        // Act
        var result = await _service.Get{{ PrefixName }}s("1", 5);

        // Assert
        result.Should().NotBeNull();
        result.Items.Should().HaveCount(5);
        result.PageInfo.HasNextPage.Should().BeTrue();
        result.PageInfo.HasPreviousPage.Should().BeFalse();
        result.PageInfo.StartPage.Should().Be("1");
        result.PageInfo.NextPage.Should().Be("2");
        result.PageInfo.PreviousPage.Should().BeNull();
        _mockValidationService.Verify(x => x.ValidatePaginationRequest(1, 5), Times.Once);
    }

    [Fact]
    public async Task Update{{ PrefixName }}_ShouldReturnUpdatedEntity_WhenValidRequest()
    {
        // Arrange
        var entityId = Guid.NewGuid();
        var request = new Update{{ PrefixName }}Input
        {
            Id = entityId.ToString(),
            Name = "Updated Name"
        };

        var existingEntity = new {{ PrefixName }}EntityBuilder()
            .WithId(entityId)
            .WithName("Original Name")
            .Generate();

        _mockRepository.Setup(x => x.FindByIdAsync(entityId))
            .ReturnsAsync(existingEntity);
        _mockRepository.Setup(x => x.Update(It.IsAny<{{ PrefixName }}Entity>()))
            .Callback<{{ PrefixName }}Entity>(e => e.Name = request.Name);
        _mockRepository.Setup(x => x.SaveChangesAsync())
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.Update{{ PrefixName }}(request);

        // Assert
        result.Should().NotBeNull();
        result.{{ PrefixName }}.Should().NotBeNull();
        result.{{ PrefixName }}.Id.Should().Be(entityId.ToString());
        result.{{ PrefixName }}.Name.Should().Be("Updated Name");
        _mockValidationService.Verify(x => x.ValidateUpdateRequest(request), Times.Once);
        _mockRepository.Verify(x => x.Update(It.IsAny<{{ PrefixName }}Entity>()), Times.Once);
        _mockRepository.Verify(x => x.SaveChangesAsync(), Times.Once);
    }

    [Fact]
    public async Task Delete{{ PrefixName }}_ShouldDeleteEntity_WhenEntityExists()
    {
        // Arrange
        var entityId = Guid.NewGuid();
        var entity = new {{ PrefixName }}EntityBuilder()
            .WithId(entityId)
            .Generate();

        _mockRepository.Setup(x => x.FindByIdAsync(entityId))
            .ReturnsAsync(entity);
        _mockRepository.Setup(x => x.Delete(entity));
        _mockRepository.Setup(x => x.SaveChangesAsync())
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.Delete{{ PrefixName }}(entityId.ToString());

        // Assert
        result.Should().NotBeNull();
        result.Success.Should().BeTrue();
        result.Message.Should().Be($"{{ PrefixName }} with ID {entityId} deleted successfully");
        _mockRepository.Verify(x => x.Delete(entity), Times.Once);
        _mockRepository.Verify(x => x.SaveChangesAsync(), Times.Once);
    }

    [Fact]
    public async Task Create{{ PrefixName }}_ShouldTrimName_BeforeSaving()
    {
        // Arrange
        var request = new Create{{ PrefixName }}Input { Name = "  Test Entity  " };
        {{ PrefixName }}Entity? capturedEntity = null;

        _mockRepository.Setup(x => x.Save(It.IsAny<{{ PrefixName }}Entity>()))
            .Callback<{{ PrefixName }}Entity>(e => capturedEntity = e);
        _mockRepository.Setup(x => x.SaveChangesAsync())
            .Returns(Task.CompletedTask);

        // Act
        await _service.Create{{ PrefixName }}(request);

        // Assert
        capturedEntity.Should().NotBeNull();
        capturedEntity!.Name.Should().Be("Test Entity");
    }
}