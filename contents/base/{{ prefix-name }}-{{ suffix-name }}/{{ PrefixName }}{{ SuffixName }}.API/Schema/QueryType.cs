using HotChocolate.Types;

namespace {{ PrefixName }}{{ SuffixName }}.API.Schema;

public class QueryType : ObjectType
{
    protected override void Configure(IObjectTypeDescriptor descriptor)
    {
        descriptor.Name("Query");
        descriptor.Description("The query root type");
    }
}

public class MutationType : ObjectType
{
    protected override void Configure(IObjectTypeDescriptor descriptor)
    {
        descriptor.Name("Mutation");
        descriptor.Description("The mutation root type");
    }
}