using HotChocolate.Types;

namespace {{ PrefixName }}{{ SuffixName }}.API.Schema;

public class {{ PrefixName }}ConnectionType : ObjectType<{{ PrefixName }}Connection>
{
    protected override void Configure(IObjectTypeDescriptor<{{ PrefixName }}Connection> descriptor)
    {
        descriptor.Name("{{ PrefixName }}Connection");
        descriptor.Description("Paginated list of {{ PrefixName }} entities");

        descriptor
            .Field(f => f.Items)
            .Type<NonNullType<ListType<NonNullType<{{ PrefixName }}Type>>>>()
            .Description("The list of {{ PrefixName }} entities");

        descriptor
            .Field(f => f.PageInfo)
            .Type<NonNullType<PageInfoType>>()
            .Description("Information about the current page");

        descriptor
            .Field(f => f.TotalCount)
            .Type<NonNullType<IntType>>()
            .Description("The total number of items");
    }
}

public class PageInfoType : ObjectType<PageInfo>
{
    protected override void Configure(IObjectTypeDescriptor<PageInfo> descriptor)
    {
        descriptor.Name("PageInfo");
        descriptor.Description("Information about pagination");

        descriptor
            .Field(f => f.HasNextPage)
            .Type<NonNullType<BooleanType>>()
            .Description("Whether there is a next page");

        descriptor
            .Field(f => f.HasPreviousPage)
            .Type<NonNullType<BooleanType>>()
            .Description("Whether there is a previous page");

        descriptor
            .Field(f => f.StartPage)
            .Type<NonNullType<StringType>>()
            .Description("The current page number");

        descriptor
            .Field(f => f.NextPage)
            .Type<StringType>()
            .Description("The next page number if available");

        descriptor
            .Field(f => f.PreviousPage)
            .Type<StringType>()
            .Description("The previous page number if available");
    }
}

public class {{ PrefixName }}Connection
{
    public required List<{{ PrefixName }}Dto> Items { get; set; }
    public required PageInfo PageInfo { get; set; }
    public required int TotalCount { get; set; }
}

public class PageInfo
{
    public required bool HasNextPage { get; set; }
    public required bool HasPreviousPage { get; set; }
    public required string StartPage { get; set; }
    public string? NextPage { get; set; }
    public string? PreviousPage { get; set; }
}