using {{ PrefixName }}{{ SuffixName }}.API;
using {{ PrefixName }}{{ SuffixName }}.API.Schema;

namespace {{ PrefixName }}{{ SuffixName }}.Core.Services;

/// <summary>
/// Service for validating requests and business rules
/// </summary>
public interface IValidationService
{
    /// <summary>
    /// Validates a {{ PrefixName }} creation request
    /// </summary>
    void ValidateCreateRequest(Create{{ PrefixName }}Input input);

    /// <summary>
    /// Validates a {{ PrefixName }} update request
    /// </summary>
    void ValidateUpdateRequest(Update{{ PrefixName }}Input input);

    /// <summary>
    /// Validates pagination parameters
    /// </summary>
    void ValidatePaginationRequest(int startPage, int pageSize);

    /// <summary>
    /// Validates an entity ID
    /// </summary>
    Guid ValidateAndParseId(string id, string fieldName = "Id");
}