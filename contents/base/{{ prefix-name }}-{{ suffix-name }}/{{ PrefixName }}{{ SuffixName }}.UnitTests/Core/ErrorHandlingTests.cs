using {{ PrefixName }}{{ SuffixName }}.API;
using {{ PrefixName }}{{ SuffixName }}.API.Schema;
using {{ PrefixName }}{{ SuffixName }}.Core;
using {{ PrefixName }}{{ SuffixName }}.Core.Services;
using {{ PrefixName }}{{ SuffixName }}.Core.Exceptions;
using {{ PrefixName }}{{ SuffixName }}.Persistence.Entities;
using {{ PrefixName }}{{ SuffixName }}.Persistence.Models;
using {{ PrefixName }}{{ SuffixName }}.Persistence.Repositories;
using {{ PrefixName }}{{ SuffixName }}.UnitTests.TestBuilders;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Microsoft.EntityFrameworkCore;
using Moq;

namespace {{ PrefixName }}{{ SuffixName }}.UnitTests.Core;

public class ErrorHandlingTests
{
    private readonly Mock<I{{ PrefixName }}Repository> _mockRepository;
    private readonly Mock<IValidationService> _mockValidationService;
    private readonly Mock<ILogger<{{ PrefixName }}{{ SuffixName }}Core>> _mockLogger;
    private readonly {{ PrefixName }}{{ SuffixName }}Core _service;

    public ErrorHandlingTests()
    {
        _mockRepository = new Mock<I{{ PrefixName }}Repository>();
        _mockValidationService = new Mock<IValidationService>();
        _mockLogger = new Mock<ILogger<{{ PrefixName }}{{ SuffixName }}Core>>();

        _service = new {{ PrefixName }}{{ SuffixName }}Core(
            _mockRepository.Object,
            _mockValidationService.Object,
            _mockLogger.Object);
    }

    [Fact]
    public async Task Create{{ PrefixName }}_ShouldThrowValidationException_WhenValidationFails()
    {
        // Arrange
        var request = new Create{{ PrefixName }}Input { Name = "" };
        _mockValidationService
            .Setup(x => x.ValidateCreateRequest(It.IsAny<Create{{ PrefixName }}Input>()))
            .Throws(new ValidationException("Name", "Name is required"));

        // Act & Assert
        var exception = await Assert.ThrowsAsync<ValidationException>(() => _service.Create{{ PrefixName }}(request));
        exception.ErrorCode.Should().Be("VALIDATION_ERROR");
        exception.ValidationErrors.Should().ContainKey("Name");
    }

    [Fact]
    public async Task Get{{ PrefixName }}_ShouldReturnNull_WhenEntityNotFound()
    {
        // Arrange
        var id = Guid.NewGuid().ToString();
        _mockValidationService
            .Setup(x => x.ValidateAndParseId(id, "Id"))
            .Returns(Guid.Parse(id));
        _mockRepository
            .Setup(x => x.FindByIdAsync(It.IsAny<Guid>()))
            .ReturnsAsync(({{ PrefixName }}Entity?)null);

        // Act
        var result = await _service.Get{{ PrefixName }}(id);

        // Assert
        result.Should().BeNull();
    }

    [Fact]
    public async Task Update{{ PrefixName }}_ShouldReturnNull_WhenEntityNotFound()
    {
        // Arrange
        var id = Guid.NewGuid();
        var request = new Update{{ PrefixName }}Input { Id = id.ToString(), Name = "Updated" };
        _mockValidationService
            .Setup(x => x.ValidateUpdateRequest(It.IsAny<Update{{ PrefixName }}Input>()))
            .Verifiable();
        _mockValidationService
            .Setup(x => x.ValidateAndParseId(id.ToString(), "Id"))
            .Returns(id);
        _mockRepository
            .Setup(x => x.FindByIdAsync(id))
            .ReturnsAsync(({{ PrefixName }}Entity?)null);

        // Act
        var result = await _service.Update{{ PrefixName }}(request);

        // Assert
        result.Should().BeNull();
    }

    [Fact]
    public async Task Delete{{ PrefixName }}_ShouldThrowEntityNotFoundException_WhenEntityNotFound()
    {
        // Arrange
        var id = Guid.NewGuid();
        _mockValidationService
            .Setup(x => x.ValidateAndParseId(id.ToString(), "Id"))
            .Returns(id);
        _mockRepository
            .Setup(x => x.FindByIdAsync(id))
            .ReturnsAsync(({{ PrefixName }}Entity?)null);

        // Act & Assert
        var exception = await Assert.ThrowsAsync<EntityNotFoundException>(() => _service.Delete{{ PrefixName }}(id.ToString()));
        exception.Message.Should().Contain(id.ToString());
    }

    [Fact]
    public async Task Create{{ PrefixName }}_ShouldThrowDataAccessException_WhenDbUpdateExceptionOccurs()
    {
        // Arrange
        var request = new Create{{ PrefixName }}Input { Name = "Duplicate Name" };
        _mockValidationService
            .Setup(x => x.ValidateCreateRequest(It.IsAny<Create{{ PrefixName }}Input>()))
            .Verifiable();
        _mockRepository
            .Setup(x => x.Save(It.IsAny<{{ PrefixName }}Entity>()));
        _mockRepository
            .Setup(x => x.SaveChangesAsync())
            .ThrowsAsync(new DbUpdateException("Duplicate key value"));

        // Act & Assert
        var exception = await Assert.ThrowsAsync<DataAccessException>(() => _service.Create{{ PrefixName }}(request));
        exception.Message.Should().Contain("Failed to save entity to database");
    }

    [Fact]
    public async Task Get{{ PrefixName }}s_ShouldHandleRepositoryException_AndThrowServiceException()
    {
        // Arrange
        _mockValidationService
            .Setup(x => x.ValidatePaginationRequest(It.IsAny<int>(), It.IsAny<int>()))
            .Verifiable();
        _mockRepository
            .Setup(x => x.FindAsync(It.IsAny<PageRequest>()))
            .ThrowsAsync(new Exception("Database error"));

        // Act & Assert
        var exception = await Assert.ThrowsAsync<DataAccessException>(() => _service.Get{{ PrefixName }}s("1", 10));
        exception.Message.Should().Contain("Failed to retrieve entities from database");
        exception.InnerException?.Message.Should().Be("Database error");
    }
}