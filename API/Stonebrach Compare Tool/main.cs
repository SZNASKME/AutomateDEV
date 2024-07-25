using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.IO;
using System.IO.Compression;
using System.Net;
using RestSharp.Authenticators;
using RestSharp;
using System.Text.Json.Nodes;
using System.Text.Json;
using JsonArray = System.Text.Json.Nodes.JsonArray;
using OfficeOpenXml.FormulaParsing.Excel.Functions.Text;
using System.Xml.Linq;
using OfficeOpenXml;
using OfficeOpenXml.FormulaParsing.Excel.Functions.Math;

namespace Stonebrach_Compare_Tool
{
    public partial class main : Form
    {
        public main()
        {
            InitializeComponent();
        }

        private void main_Load(object sender, EventArgs e)
        {
            //Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            //using (var package = new ExcelPackage(new FileInfo(@"D:\Stonebranch\TTB\API\Workflow_Update_DWH.xlsx")))
            //{
            //    ExcelWorksheet workSheet = package.Workbook.Worksheets[1];
            //    var start = workSheet.Dimension.Start;
            //    var end = workSheet.Dimension.End;
            //    for (int row = start.Row+1 ; row <= end.Row; row++)
            //    { // Row by row...
            //        var JobName = workSheet.Cells[row, 5].Text;
            //        var Task_Time = workSheet.Cells[row, 14].Text;
            //        //Debug.WriteLine(value);
            //        var client = new RestClient("http://172.16.1.85:8080/uc/resources/task?taskname=" + JobName);
            //        client.Authenticator = new HttpBasicAuthenticator("ops.admin", "p@ssw0rd");

            //        var request = new RestRequest();
            //        request.AddHeader("Accept", "application/json");
            //        request.AddHeader("Content-type", "application/json");


            //        var responseJson = client.Get(request);
            //        var data = JsonSerializer.Deserialize<JsonNode>(responseJson.Content!)!;

            //        data["twWaitTime"] = Task_Time.ToString();
            //        data["twWaitType"] = "Relative Time";

            //        var JsonBody = Convert.ToString(data);
            //    }

            }
            
            //var data = JsonSerializer.Deserialize<JsonNode>(responseJson.Content!)!;
            //var data_arr = data as JsonArray;
     
           // data["twWaitTime"] = "07:00";
            //data["twWaitType"] = "Relative Time";

            //var JsonBody = Convert.ToString(data);

            //var client2 = new RestClient("http://172.16.1.86:8080/uc/resources/task");
            //client2.Authenticator = new HttpBasicAuthenticator("ops.admin", "p@ssw0rd");
            //var request2 = new RestRequest();
            //request2.AddHeader("Content-Type", "application/json; charset=utf-8");
            //request2.AddJsonBody(JsonBody);
            //var response = client2.Put(request2);
          




            //WebClient webClient = new WebClient();
            //var client = new WebClient();
            //if (!webClient.DownloadString("http://localhost:8080/version/version.txt").Contains("1.0.0"))
            //{
            //    if (MessageBox.Show("A new update is available! Do you want to download it?", "Demo", MessageBoxButtons.YesNo, MessageBoxIcon.Question) == DialogResult.Yes)
            //    {
            //        try
            //        {
            //            /*   if (File.Exists(@".\MyAppSetup.msi")) 
            //               {
            //                   File.Delete(@".\MyAppSetup.msi"); 

            //               }*/
            //            File.Delete(@".\test\version.txt");
            //            client.DownloadFile("http://localhost:8080/version/version.zip", @"version.zip");
            //            string zipPath = @".\version.zip";
            //            string extractPath = @".\Test";
            //            ZipFile.ExtractToDirectory(zipPath, extractPath);
            //       /*     Process process = new Process();
            //            process.StartInfo.FileName = "msiexec.exe";
            //            process.StartInfo.Arguments = string.Format("/i MyAppSetup.msi");
            //            this.Close();
            //            process.Start();*/

            //            Application.Restart();
            //            Environment.Exit(0);
            //        }
            //        catch
            //        {
            //        }
            //    }
            //}




            //var version = System.Reflection.Assembly.GetExecutingAssembly().GetName().Version;
            //Debug.WriteLine(version);
        }
    }
}
