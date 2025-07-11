using {{ PrefixName }}{{ SuffixName }}.API;
using {{ PrefixName }}{{ SuffixName }}.API.Schema;
using {{ PrefixName }}{{ SuffixName }}.Core.Exceptions;
using Microsoft.Extensions.Logging;
using System.Text.RegularExpressions;

namespace {{ PrefixName }}{{ SuffixName }}.Core.Services;

/// <summary>
/// Service for validating requests and business rules
/// </summary>
public class ValidationService : IValidationService
{
    private readonly ILogger<ValidationService> _logger;
    private static readonly Regex NamePattern = new(@"^[a-zA-Z0-9\s\-_\.]{1,100}$", RegexOptions.Compiled);

    public ValidationService(ILogger<ValidationService> logger)
    {
        _logger = logger;
    }

    public void ValidateCreateRequest(Create{{ PrefixName }}Input input)
    {
        var errors = new Dictionary<string, string[]>();

        if (input == null)
        {
            throw new ValidationException("input", "Input cannot be null.");
        }

        // Validate Name
        if (string.IsNullOrWhiteSpace(input.Name))
        {
            errors["Name"] = new[] { "Name is required and cannot be empty." };
        }
        else if (input.Name.Length > 100)
        {
            errors["Name"] = new[] { "Name cannot exceed 100 characters." };
        }
        else if (!NamePattern.IsMatch(input.Name))
        {
            errors["Name"] = new[] { "Name contains invalid characters. Only letters, numbers, spaces, hyphens, underscores, and dots are allowed." };
        }

        if (errors.Any())
        {
            _logger.LogWarning("Validation failed for create request: {@ValidationErrors}", errors);
            throw new ValidationException(errors);
        }

        _logger.LogDebug("Create request validation passed for: {Name}", input.Name);
    }

    public void ValidateUpdateRequest(Update{{ PrefixName }}Input input)
    {
        var errors = new Dictionary<string, string[]>();

        if (input == null)
        {
            throw new ValidationException("input", "Input cannot be null.");
        }

        // Validate ID
        if (string.IsNullOrWhiteSpace(input.Id))
        {
            errors["Id"] = new[] { "ID is required for update requests." };
        }
        else
        {
            try
            {
                Guid.Parse(input.Id);
            }
            catch (FormatException)
            {
                errors["Id"] = new[] { "ID must be a valid GUID format." };
            }
        }

        // Validate Name
        if (string.IsNullOrWhiteSpace(input.Name))
        {
            errors["Name"] = new[] { "Name is required and cannot be empty." };
        }
        else if (input.Name.Length > 100)
        {
            errors["Name"] = new[] { "Name cannot exceed 100 characters." };
        }
        else if (!NamePattern.IsMatch(input.Name))
        {
            errors["Name"] = new[] { "Name contains invalid characters. Only letters, numbers, spaces, hyphens, underscores, and dots are allowed." };
        }

        if (errors.Any())
        {
            _logger.LogWarning("Validation failed for update request: {@ValidationErrors}", errors);
            throw new ValidationException(errors);
        }

        _logger.LogDebug("Update request validation passed for: {Id} - {Name}", input.Id, input.Name);
    }

    public void ValidatePaginationRequest(int startPage, int pageSize)
    {
        var errors = new Dictionary<string, string[]>();

        if (startPage < 1)
        {
            errors["StartPage"] = new[] { "StartPage must be greater than 0." };
        }

        if (pageSize < 1)
        {
            errors["PageSize"] = new[] { "PageSize must be greater than 0." };
        }
        else if (pageSize > 1000)
        {
            errors["PageSize"] = new[] { "PageSize cannot exceed 1000." };
        }

        if (errors.Any())
        {
            _logger.LogWarning("Validation failed for pagination request: {@ValidationErrors}", errors);
            throw new ValidationException(errors);
        }

        _logger.LogDebug("Pagination request validation passed: StartPage={StartPage}, PageSize={PageSize}",
            startPage, pageSize);
    }

    public Guid ValidateAndParseId(string id, string fieldName = "Id")
    {
        if (string.IsNullOrWhiteSpace(id))
        {
            throw new ValidationException(fieldName, $"{fieldName} is required and cannot be empty.");
        }

        try
        {
            var parsedId = Guid.Parse(id);

            if (parsedId == Guid.Empty)
            {
                throw new ValidationException(fieldName, $"{fieldName} cannot be an empty GUID.");
            }

            return parsedId;
        }
        catch (FormatException ex)
        {
            _logger.LogWarning(ex, "Invalid GUID format for {FieldName}: {Id}", fieldName, id);
            throw new ValidationException(fieldName, $"{fieldName} must be a valid GUID format.");
        }
    }
}