using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Threading.Tasks;
using RestSharp;
using RestSharp.Authenticators;
using JsonArray = System.Text.Json.Nodes.JsonArray;

namespace Stonebrach_Compare_Tool
{
    internal class http_request
    {
        public JsonArray Job_Detail(string WF_Name)
        {
            var client = new RestClient("http://172.16.1.86:8080/uc/resources/task/listadv?taskname=" + WF_Name);
            client.Authenticator = new HttpBasicAuthenticator("ops.admin", "p@ssw0rd");

            var request = new RestRequest();
            request.AddHeader("Accept", "application/json");
            request.AddHeader("Content-type", "application/json");

            var responseJson = client.Get(request);
            var data = JsonSerializer.Deserialize<JsonNode>(responseJson.Content!)!;
            var data_arr = data as JsonArray;

            return data_arr;

        }
    }
}
