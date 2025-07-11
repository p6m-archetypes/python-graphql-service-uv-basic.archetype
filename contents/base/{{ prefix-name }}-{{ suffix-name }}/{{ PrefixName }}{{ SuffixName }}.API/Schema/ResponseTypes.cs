using HotChocolate.Types;

namespace {{ PrefixName }}{{ SuffixName }}.API.Schema;

public class Create{{ PrefixName }}ResponseType : ObjectType<Create{{ PrefixName }}Response>
{
    protected override void Configure(IObjectTypeDescriptor<Create{{ PrefixName }}Response> descriptor)
    {
        descriptor.Name("Create{{ PrefixName }}Response");
        descriptor.Description("Response for creating a {{ PrefixName }}");

        descriptor
            .Field(f => f.{{ PrefixName }})
            .Type<NonNullType<{{ PrefixName }}Type>>()
            .Description("The created {{ PrefixName }}");
    }
}

public class Update{{ PrefixName }}ResponseType : ObjectType<Update{{ PrefixName }}Response>
{
    protected override void Configure(IObjectTypeDescriptor<Update{{ PrefixName }}Response> descriptor)
    {
        descriptor.Name("Update{{ PrefixName }}Response");
        descriptor.Description("Response for updating a {{ PrefixName }}");

        descriptor
            .Field(f => f.{{ PrefixName }})
            .Type<NonNullType<{{ PrefixName }}Type>>()
            .Description("The updated {{ PrefixName }}");
    }
}

public class Delete{{ PrefixName }}ResponseType : ObjectType<Delete{{ PrefixName }}Response>
{
    protected override void Configure(IObjectTypeDescriptor<Delete{{ PrefixName }}Response> descriptor)
    {
        descriptor.Name("Delete{{ PrefixName }}Response");
        descriptor.Description("Response for deleting a {{ PrefixName }}");

        descriptor
            .Field(f => f.Success)
            .Type<NonNullType<BooleanType>>()
            .Description("Whether the deletion was successful");

        descriptor
            .Field(f => f.Message)
            .Type<StringType>()
            .Description("Optional message about the deletion");
    }
}

public class Create{{ PrefixName }}Response
{
    public required {{ PrefixName }}Dto {{ PrefixName }} { get; set; }
}

public class Update{{ PrefixName }}Response
{
    public required {{ PrefixName }}Dto {{ PrefixName }} { get; set; }
}

public class Delete{{ PrefixName }}Response
{
    public required bool Success { get; set; }
    public string? Message { get; set; }
}