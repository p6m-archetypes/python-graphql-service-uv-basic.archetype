using {{ PrefixName }}{{ SuffixName }}.API.Schema;

namespace {{ PrefixName }}{{ SuffixName }}.API;

public interface I{{ PrefixName }}{{ SuffixName }}
{
    Task<Create{{ PrefixName }}Response> Create{{ PrefixName }}(Create{{ PrefixName }}Input input);
    Task<{{ PrefixName }}Connection> Get{{ PrefixName }}s(string? startPage, int? pageSize);
    Task<{{ PrefixName }}Dto?> Get{{ PrefixName }}(string id);
    Task<Update{{ PrefixName }}Response> Update{{ PrefixName }}(Update{{ PrefixName }}Input input);
    Task<Delete{{ PrefixName }}Response> Delete{{ PrefixName }}(string id);
}