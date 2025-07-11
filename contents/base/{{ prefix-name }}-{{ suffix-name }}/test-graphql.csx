#!/usr/bin/env dotnet-script

using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

var client = new HttpClient();
var query = @"{
    ""query"": ""{ __schema { queryType { name } } }""
}";

var content = new StringContent(query, Encoding.UTF8, "application/json");
var response = await client.PostAsync("http://localhost:5041/graphql", content);

Console.WriteLine($"Status: {response.StatusCode}");
Console.WriteLine($"Content: {await response.Content.ReadAsStringAsync()}");