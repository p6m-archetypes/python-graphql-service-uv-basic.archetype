using HotChocolate.Types;

namespace {{ PrefixName }}{{ SuffixName }}.API.Schema;

public class {{ PrefixName }}Type : ObjectType<{{ PrefixName }}Dto>
{
    protected override void Configure(IObjectTypeDescriptor<{{ PrefixName }}Dto> descriptor)
    {
        descriptor.Name("{{ PrefixName }}");
        descriptor.Description("A {{ PrefixName }} entity");

        descriptor
            .Field(f => f.Id)
            .Type<StringType>()
            .Description("The unique identifier of the {{ PrefixName }}");

        descriptor
            .Field(f => f.Name)
            .Type<NonNullType<StringType>>()
            .Description("The name of the {{ PrefixName }}");
    }
}

public class {{ PrefixName }}Dto
{
    public string? Id { get; set; }
    public required string Name { get; set; }
}