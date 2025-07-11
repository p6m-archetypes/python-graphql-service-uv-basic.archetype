using {{ PrefixName }}{{ SuffixName }}.API;
using {{ PrefixName }}{{ SuffixName }}.API.Schema;
using {{ PrefixName }}{{ SuffixName }}.API.Logger;
using {{ PrefixName }}{{ SuffixName }}.Core.Services;
using {{ PrefixName }}{{ SuffixName }}.Core.Exceptions;
using {{ PrefixName }}{{ SuffixName }}.Persistence.Entities;
using {{ PrefixName }}{{ SuffixName }}.Persistence.Models;
using {{ PrefixName }}{{ SuffixName }}.Persistence.Repositories;
using Microsoft.Extensions.Logging;
using Microsoft.EntityFrameworkCore;
using System.Diagnostics;

namespace {{ PrefixName }}{{ SuffixName }}.Core;

public class {{ PrefixName }}{{ SuffixName }}Core : I{{ PrefixName }}{{ SuffixName }}
{
    private readonly I{{ PrefixName }}Repository _{{ prefixName }}Repository;
    private readonly IValidationService _validationService;
    private readonly ILogger<{{ PrefixName }}{{ SuffixName }}Core> _logger;

    public {{ PrefixName }}{{ SuffixName }}Core(
        I{{ PrefixName }}Repository {{ prefixName }}Repository,
        IValidationService validationService,
        ILogger<{{ PrefixName }}{{ SuffixName }}Core> logger)
    {
        _{{ prefixName }}Repository = {{ prefixName }}Repository;
        _validationService = validationService;
        _logger = logger;
    }
    public async Task<Create{{ PrefixName }}Response> Create{{ PrefixName }}(Create{{ PrefixName }}Input input)
    {
        using var scope = _logger.BeginScope("Operation: {Operation}, Entity: {EntityType}",
            "Create{{ PrefixName }}", "{{ PrefixName }}");

        var stopwatch = Stopwatch.StartNew();

        try
        {
            // Validate input
            _validationService.ValidateCreateRequest(input);

            _logger.LogDebug("Creating {{ PrefixName }} entity: {Name}", input.Name);

            try
            {
                var {{ prefixName }} = new {{ PrefixName }}Entity
                {
                    Name = input.Name.Trim()
                };

                _{{ prefixName }}Repository.Save({{ prefixName }});
                await _{{ prefixName }}Repository.SaveChangesAsync();

                stopwatch.Stop();
                _logger.LogInformation("Successfully created {{ PrefixName }} entity {Id} in {Duration}ms",
                    {{ prefixName }}.Id, stopwatch.ElapsedMilliseconds);

                return new Create{{ PrefixName }}Response
                {
                    {{ PrefixName }} = new {{ PrefixName }}Dto
                    {
                        Id = {{ prefixName }}.Id.ToString(),
                        Name = {{ prefixName }}.Name
                    }
                };
            }
            catch (DbUpdateException ex)
            {
                stopwatch.Stop();
                _logger.LogError(ex, "Database error creating {{ PrefixName }} entity {Name} after {Duration}ms",
                    input.Name, stopwatch.ElapsedMilliseconds);
                throw new DataAccessException("Create", "Failed to save entity to database.", ex);
            }
            catch (Exception ex)
            {
                stopwatch.Stop();
                _logger.LogError(ex, "Unexpected error creating {{ PrefixName }} entity {Name} after {Duration}ms",
                    input.Name, stopwatch.ElapsedMilliseconds);
                throw;
            }
        }
        catch (ValidationException ex)
        {
            stopwatch.Stop();
            _logger.LogWarning("Validation failed for Create{{ PrefixName }} {Name}: {Error} after {Duration}ms",
                input?.Name, ex.Message, stopwatch.ElapsedMilliseconds);
            throw;
        }
        catch (DataAccessException)
        {
            // Re-throw data access exceptions as-is
            throw;
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            _logger.LogError(ex, "Create{{ PrefixName }} failed for {Name} after {Duration}ms",
                input?.Name, stopwatch.ElapsedMilliseconds);
            throw new DataAccessException("Create", "An unexpected error occurred while creating the entity.", ex);
        }
    }

    public async Task<{{ PrefixName }}Connection> Get{{ PrefixName }}s(string? startPage, int? pageSize)
    {
        using var scope = _logger.BeginScope("Operation: {Operation}, Entity: {EntityType}",
            "Get{{ PrefixName }}s", "{{ PrefixName }}");

        var stopwatch = Stopwatch.StartNew();

        try
        {
            // Validate input
            var parsedStartPage = int.TryParse(startPage, out var sp) ? sp : 1;
            var parsedPageSize = pageSize ?? 10;
            _validationService.ValidatePaginationRequest(parsedStartPage, parsedPageSize);

            parsedStartPage = Math.Max(1, parsedStartPage);
            parsedPageSize = Math.Max(Math.Min(parsedPageSize, 100), 1);

            _logger.LogDebug("Fetching {{ PrefixName }} entities: page {StartPage}, size {PageSize}", parsedStartPage, parsedPageSize);

            try
            {
                PageRequest pageRequest = new PageRequest
                {
                    PageSize = parsedPageSize,
                    StartPage = parsedStartPage
                };

                var page = await _{{ prefixName }}Repository.FindAsync(pageRequest);

                var items = page.Items.Select({{ prefixName }} => new {{ PrefixName }}Dto
                {
                    Id = {{ prefixName }}.Id.ToString(),
                    Name = {{ prefixName }}.Name
                }).ToList();

                var totalPages = (int)Math.Ceiling((double)page.TotalElements / parsedPageSize);
                var hasNextPage = parsedStartPage < totalPages;
                var hasPreviousPage = parsedStartPage > 1;

                var response = new {{ PrefixName }}Connection
                {
                    Items = items,
                    PageInfo = new PageInfo
                    {
                        HasNextPage = hasNextPage,
                        HasPreviousPage = hasPreviousPage,
                        StartPage = parsedStartPage.ToString(),
                        NextPage = hasNextPage ? (parsedStartPage + 1).ToString() : null,
                        PreviousPage = hasPreviousPage ? (parsedStartPage - 1).ToString() : null
                    },
                    TotalCount = (int)page.TotalElements
                };

                stopwatch.Stop();
                _logger.LogInformation("Fetched {Count} {{ PrefixName }} entities (total: {Total}) in {Duration}ms",
                    page.Items.Count, page.TotalElements, stopwatch.ElapsedMilliseconds);

                return response;
            }
            catch (Exception ex)
            {
                stopwatch.Stop();
                _logger.LogError(ex, "Database error fetching {{ PrefixName }} entities page {StartPage}, size {PageSize} after {Duration}ms",
                    startPage, pageSize, stopwatch.ElapsedMilliseconds);
                throw new DataAccessException("Read", "Failed to retrieve entities from database.", ex);
            }
        }
        catch (ValidationException ex)
        {
            stopwatch.Stop();
            _logger.LogWarning("Validation failed for Get{{ PrefixName }}s page {StartPage}, size {PageSize}: {Error} after {Duration}ms",
                startPage, pageSize, ex.Message, stopwatch.ElapsedMilliseconds);
            throw;
        }
        catch (DataAccessException)
        {
            // Re-throw data access exceptions as-is
            throw;
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            _logger.LogError(ex, "Get{{ PrefixName }}s failed for page {StartPage}, size {PageSize} after {Duration}ms",
                startPage, pageSize, stopwatch.ElapsedMilliseconds);
            throw new DataAccessException("Read", "An unexpected error occurred while retrieving entities.", ex);
        }
    }

    public async Task<{{ PrefixName }}Dto?> Get{{ PrefixName }}(string id)
    {
        using var scope = _logger.BeginScope("Operation: {Operation}, Entity: {EntityType}, Id: {Id}",
            "Get{{ PrefixName }}", "{{ PrefixName }}", id);

        var stopwatch = Stopwatch.StartNew();

        try
        {
            // Validate and parse ID
            var entityId = _validationService.ValidateAndParseId(id);

            _logger.LogDebug("Fetching {{ PrefixName }} entity by ID: {Id}", entityId);

            try
            {
                var {{ prefixName }} = await _{{ prefixName }}Repository.FindByIdAsync(entityId);
                if ({{ prefixName }} == null)
                {
                    stopwatch.Stop();
                    _logger.LogWarning("{{ PrefixName }} entity not found: {Id} after {Duration}ms",
                        entityId, stopwatch.ElapsedMilliseconds);
                    return null;
                }

                stopwatch.Stop();
                _logger.LogDebug("Found {{ PrefixName }} entity {Id} ({Name}) in {Duration}ms",
                    {{ prefixName }}.Id, {{ prefixName }}.Name, stopwatch.ElapsedMilliseconds);

                return new {{ PrefixName }}Dto
                {
                    Id = {{ prefixName }}.Id.ToString(),
                    Name = {{ prefixName }}.Name
                };
            }
            catch (EntityNotFoundException)
            {
                // For GraphQL, return null when entity not found  
                return null;
            }
            catch (Exception ex)
            {
                stopwatch.Stop();
                _logger.LogError(ex, "Database error fetching {{ PrefixName }} entity {Id} after {Duration}ms",
                    entityId, stopwatch.ElapsedMilliseconds);
                throw new DataAccessException("Read", "Failed to retrieve entity from database.", ex);
            }
        }
        catch (ValidationException ex)
        {
            stopwatch.Stop();
            _logger.LogWarning("Validation failed for Get{{ PrefixName }} {Id}: {Error} after {Duration}ms",
                id, ex.Message, stopwatch.ElapsedMilliseconds);
            throw;
        }
        catch (EntityNotFoundException)
        {
            // Re-throw entity not found exceptions as-is
            throw;
        }
        catch (DataAccessException)
        {
            // Re-throw data access exceptions as-is
            throw;
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            _logger.LogError(ex, "Get{{ PrefixName }} failed for {Id} after {Duration}ms",
                id, stopwatch.ElapsedMilliseconds);
            throw new DataAccessException("Read", "An unexpected error occurred while retrieving the entity.", ex);
        }
    }

    public async Task<Update{{ PrefixName }}Response> Update{{ PrefixName }}(Update{{ PrefixName }}Input input)
    {
        using var scope = _logger.BeginScope("Operation: {Operation}, Entity: {EntityType}, Id: {Id}",
            "Update{{ PrefixName }}", "{{ PrefixName }}", input.Id);

        var stopwatch = Stopwatch.StartNew();

        try
        {
            // Validate input
            _validationService.ValidateUpdateRequest(input);
            var entityId = _validationService.ValidateAndParseId(input.Id);

            _logger.LogDebug("Updating {{ PrefixName }} entity: {Id} - {Name}", entityId, input.Name);

            try
            {
                var entity = await _{{ prefixName }}Repository.FindByIdAsync(entityId);
                if (entity == null)
                {
                    stopwatch.Stop();
                    _logger.LogWarning("{{ PrefixName }} entity not found for update: {Id} after {Duration}ms",
                        entityId, stopwatch.ElapsedMilliseconds);
                    throw new EntityNotFoundException("{{ PrefixName }}", entityId.ToString());
                }

                // Check for business rules
                if (entity.Name == input.Name.Trim())
                {
                    stopwatch.Stop();
                    _logger.LogDebug("No changes detected for {{ PrefixName }} entity {Id} after {Duration}ms",
                        entityId, stopwatch.ElapsedMilliseconds);

                    return new Update{{ PrefixName }}Response
                    {
                        {{ PrefixName }} = new {{ PrefixName }}Dto
                        {
                            Id = entity.Id.ToString(),
                            Name = entity.Name
                        }
                    };
                }

                var oldName = entity.Name;
                entity.Name = input.Name.Trim();

                _{{ prefixName }}Repository.Update(entity);
                await _{{ prefixName }}Repository.SaveChangesAsync();

                stopwatch.Stop();
                _logger.LogInformation("Updated {{ PrefixName }} entity {Id} from '{OldName}' to '{NewName}' in {Duration}ms",
                    entity.Id, oldName, entity.Name, stopwatch.ElapsedMilliseconds);

                return new Update{{ PrefixName }}Response
                {
                    {{ PrefixName }} = new {{ PrefixName }}Dto
                    {
                        Id = entity.Id.ToString(),
                        Name = entity.Name
                    }
                };
            }
            catch (EntityNotFoundException)
            {
                // For GraphQL, return null when entity not found  
                return null;
            }
            catch (DbUpdateConcurrencyException ex)
            {
                stopwatch.Stop();
                _logger.LogWarning(ex, "Concurrency conflict updating {{ PrefixName }} entity {Id} after {Duration}ms",
                    entityId, stopwatch.ElapsedMilliseconds);
                throw new DataAccessException("Update", "The entity was modified by another user. Please refresh and try again.", ex);
            }
            catch (DbUpdateException ex)
            {
                stopwatch.Stop();
                _logger.LogError(ex, "Database error updating {{ PrefixName }} entity {Id} after {Duration}ms",
                    entityId, stopwatch.ElapsedMilliseconds);
                throw new DataAccessException("Update", "Failed to update entity in database.", ex);
            }
            catch (Exception ex)
            {
                stopwatch.Stop();
                _logger.LogError(ex, "Unexpected error updating {{ PrefixName }} entity {Id} after {Duration}ms",
                    entityId, stopwatch.ElapsedMilliseconds);
                throw;
            }
        }
        catch (ValidationException ex)
        {
            stopwatch.Stop();
            _logger.LogWarning("Validation failed for Update{{ PrefixName }} {Id}: {Error} after {Duration}ms",
                input?.Id, ex.Message, stopwatch.ElapsedMilliseconds);
            throw;
        }
        catch (EntityNotFoundException)
        {
            // Re-throw entity not found exceptions as-is
            throw;
        }
        catch (DataAccessException)
        {
            // Re-throw data access exceptions as-is
            throw;
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            _logger.LogError(ex, "Update{{ PrefixName }} failed for {Id} after {Duration}ms",
                input?.Id, stopwatch.ElapsedMilliseconds);
            throw new DataAccessException("Update", "An unexpected error occurred while updating the entity.", ex);
        }
    }

    public async Task<Delete{{ PrefixName }}Response> Delete{{ PrefixName }}(string id)
    {
        using var scope = _logger.BeginScope("Operation: {Operation}, Entity: {EntityType}, Id: {Id}",
            "Delete{{ PrefixName }}", "{{ PrefixName }}", id);

        var stopwatch = Stopwatch.StartNew();

        try
        {
            // Validate and parse ID
            var entityId = _validationService.ValidateAndParseId(id);

            _logger.LogDebug("Deleting {{ PrefixName }} entity by ID: {Id}", entityId);

            try
            {
                var {{ prefixName }} = await _{{ prefixName }}Repository.FindByIdAsync(entityId);
                if ({{ prefixName }} == null)
                {
                    stopwatch.Stop();
                    _logger.LogWarning("{{ PrefixName }} entity not found for deletion: {Id} after {Duration}ms",
                        entityId, stopwatch.ElapsedMilliseconds);
                    throw new EntityNotFoundException("{{ PrefixName }}", entityId.ToString());
                }

                var entityName = {{ prefixName }}.Name; // Capture before deletion
                _{{ prefixName }}Repository.Delete({{ prefixName }});
                await _{{ prefixName }}Repository.SaveChangesAsync();

                stopwatch.Stop();
                _logger.LogInformation("Deleted {{ PrefixName }} entity {Id} ('{Name}') in {Duration}ms",
                    {{ prefixName }}.Id, entityName, stopwatch.ElapsedMilliseconds);

                return new Delete{{ PrefixName }}Response
                {
                    Success = true,
                    Message = $"{{ PrefixName }} with ID {entityId} deleted successfully"
                };
            }
            catch (EntityNotFoundException)
            {
                // For GraphQL, return error response when entity not found  
                stopwatch.Stop();
                _logger.LogWarning("{{ PrefixName }} entity not found for deletion: {Id} after {Duration}ms",
                    entityId, stopwatch.ElapsedMilliseconds);
                throw;
            }
            catch (DbUpdateException ex)
            {
                stopwatch.Stop();
                _logger.LogError(ex, "Database error deleting {{ PrefixName }} entity {Id} after {Duration}ms",
                    entityId, stopwatch.ElapsedMilliseconds);
                throw new DataAccessException("Delete", "Failed to delete entity from database.", ex);
            }
            catch (Exception ex)
            {
                stopwatch.Stop();
                _logger.LogError(ex, "Unexpected error deleting {{ PrefixName }} entity {Id} after {Duration}ms",
                    entityId, stopwatch.ElapsedMilliseconds);
                throw;
            }
        }
        catch (ValidationException ex)
        {
            stopwatch.Stop();
            _logger.LogWarning("Validation failed for Delete{{ PrefixName }} {Id}: {Error} after {Duration}ms",
                id, ex.Message, stopwatch.ElapsedMilliseconds);
            throw;
        }
        catch (EntityNotFoundException)
        {
            // Re-throw entity not found exceptions as-is
            throw;
        }
        catch (DataAccessException)
        {
            // Re-throw data access exceptions as-is
            throw;
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            _logger.LogError(ex, "Delete{{ PrefixName }} failed for {Id} after {Duration}ms",
                id, stopwatch.ElapsedMilliseconds);
            throw new DataAccessException("Delete", "An unexpected error occurred while deleting the entity.", ex);
        }
    }

}