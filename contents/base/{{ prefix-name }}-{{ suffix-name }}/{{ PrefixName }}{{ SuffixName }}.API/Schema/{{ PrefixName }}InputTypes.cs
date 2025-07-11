using HotChocolate.Types;

namespace {{ PrefixName }}{{ SuffixName }}.API.Schema;

public class Create{{ PrefixName }}InputType : InputObjectType<Create{{ PrefixName }}Input>
{
    protected override void Configure(IInputObjectTypeDescriptor<Create{{ PrefixName }}Input> descriptor)
    {
        descriptor.Name("Create{{ PrefixName }}Input");
        descriptor.Description("Input for creating a new {{ PrefixName }}");

        descriptor
            .Field(f => f.Name)
            .Type<NonNullType<StringType>>()
            .Description("The name of the {{ PrefixName }}");
    }
}

public class Update{{ PrefixName }}InputType : InputObjectType<Update{{ PrefixName }}Input>
{
    protected override void Configure(IInputObjectTypeDescriptor<Update{{ PrefixName }}Input> descriptor)
    {
        descriptor.Name("Update{{ PrefixName }}Input");
        descriptor.Description("Input for updating an existing {{ PrefixName }}");

        descriptor
            .Field(f => f.Id)
            .Type<NonNullType<StringType>>()
            .Description("The unique identifier of the {{ PrefixName }} to update");

        descriptor
            .Field(f => f.Name)
            .Type<NonNullType<StringType>>()
            .Description("The new name of the {{ PrefixName }}");
    }
}

public class Create{{ PrefixName }}Input
{
    public required string Name { get; set; }
}

public class Update{{ PrefixName }}Input
{
    public required string Id { get; set; }
    public required string Name { get; set; }
}