using RestSharp;
using System.IO;
using System;
using System.Net.Http;
using RestSharp.Authenticators;
using static System.Windows.Forms.VisualStyles.VisualStyleElement.StartPanel;
using System.Text.Json.Nodes;
using System.Text.Json;
using System.Runtime.InteropServices;
using JsonArray = System.Text.Json.Nodes.JsonArray;
using System.ComponentModel;
using System.Windows.Forms;
using System.Data;
using OfficeOpenXml;
using System.Text;
using System.Diagnostics;
using OfficeOpenXml.Utils;

namespace Stonebrach_Compare_Tool
{
    public partial class Form1 : Form
    {
        private static readonly HttpClient client = new HttpClient();
        public Form1()
        {
            InitializeComponent();

        }
        private void Calculate(int i)
        {
            double pow = Math.Pow(i, i);
        }
        private void backgroundWorker1_ProgressChanged(object sender, ProgressChangedEventArgs e)
        {
            progressBar1.Value = e.ProgressPercentage;
        }

        private void backgroundWorker1_RunWorkerCompleted(object sender, RunWorkerCompletedEventArgs e)
        {
            // TODO: do something with final calculation.
        }
        private void backgroundWorker1_DoWork(object sender, DoWorkEventArgs e)
        {
            DataTable dtTable = new DataTable("sbtasklist");
            this.Invoke(new MethodInvoker(delegate ()
            {
                button1.Enabled = false;
                listBox1.Items.Add("Retrives Task Detail From Stonebranch....");

                //Create Column Header
                dtTable.Columns.Add(new DataColumn("Jobname", typeof(string)));
                dtTable.Columns.Add(new DataColumn("Type", typeof(string)));
                dtTable.Columns.Add(new DataColumn("Agent", typeof(string)));
                dtTable.Columns.Add(new DataColumn("Agent Cluster", typeof(string)));
                dtTable.Columns.Add(new DataColumn("Condition", typeof(string)));
                //dtTable.Columns.Add(new DataColumn("Email", typeof(string)));
            }));


            var client = new RestClient("http://172.16.1.86:8080/uc/resources/task/listadv?taskname=CARD_SCS_CFR_DAILY_PUT_B");
            client.Authenticator = new HttpBasicAuthenticator("ops.admin", "p@ssw0rd");

            var request = new RestRequest();
            request.AddHeader("Accept", "application/json");
            request.AddHeader("Content-type", "application/json");
            var cancellationTokenSource = new CancellationTokenSource();
            var responseJson = client.Get(request);
            var options = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            };
            var data = JsonSerializer.Deserialize<JsonNode>(responseJson.Content!)!;

            var arr = data as JsonArray;
            //Console.WriteLine(arr.Count);
            //Console.WriteLine(data[0]["type"]);


            var countitem = 0;
            var backgroundWorker = sender as BackgroundWorker;
            foreach (var item in arr)
            {
                Thread.Sleep(30);
                this.Invoke(new MethodInvoker(delegate ()
                {
                    listBox1.Items.Add("Task Name : " + item["name"]);
                    listBox1.TopIndex = listBox1.Items.Count - 1;
                    if (item["type"].ToString() == "taskUniversal")
                    {
                        dtTable.Rows.Add(item["name"], item["type"], item["agent"], item["agentCluster"], "");
                    }
                    else //Workflow
                    {
                        var condition_json = JsonSerializer.Deserialize<JsonNode>(item["workflowEdges"]);
                        var condition_arr = condition_json as JsonArray;
                        //Console.WriteLine(condition_list.Count());
                        Debug.WriteLine(condition_arr.Count);
                        foreach (var condition in condition_arr)
                        {


                        }
                        dtTable.Rows.Add(item["name"], item["type"], "", "", "");

                    }

                }));


                //Console.WriteLine(item["name"] + Environment.NewLine);
                Calculate(countitem);
                backgroundWorker1.ReportProgress((countitem * 100) / arr.Count);
                countitem = countitem + 1;

            }

            this.Invoke(new MethodInvoker(delegate ()
            {

                button1.Enabled = true;
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                using (var package = new ExcelPackage())
                {
                    var workbook = package.Workbook;

                    //*** Sheet 1
                    var worksheet = workbook.Worksheets.Add("Sheet1");
                    worksheet.Cells["A1"].LoadFromDataTable(dtTable, true);
                    worksheet.Cells[worksheet.Dimension.Address].AutoFitColumns();

                    package.SaveAs(new FileInfo(@"D:/DotNet Project/Stonebrach Compare Tool/demo.xlsx"));
                }

            }));



            /*var backgroundWorker = sender as BackgroundWorker;
            for (int j = 0; j < 100000; j++)
            {
                Calculate(j);
                backgroundWorker1.ReportProgress((j * 100) / 100000);
            }*/

        }
        private void button1_Click(object sender, EventArgs e)
        {

            progressBar1.Maximum = 100;
            progressBar1.Step = 1;
            progressBar1.Value = 0;
            backgroundWorker1.RunWorkerAsync();



        }

        private void Form1_Load(object sender, EventArgs e)
        {
            AllocConsole();
        }
        [DllImport("kernel32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        static extern bool AllocConsole();



        private void button2_Click_1(object sender, EventArgs e)
        {

            //Get Task
            var http_req = new http_request();
            var response = http_req.Job_Detail("CARD_SCS_CFR_DAILY_PUT_B");
            //Debug.WriteLine(response_arr.Count);

            //Get Workflow
            response = http_req.Job_Detail("CARD_ACS_DACS_CREDIT.D.C2D_C");
            //response_arr = response[0]["workflowEdges"] as JsonArray;
            //Debug.WriteLine(response_arr.Count);


        }

        private void button3_Click(object sender, EventArgs e)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            DataTable dt = new DataTable();

            utility utility = new utility();
            dt = utility.ExceltoDatatable();

            var dt_filter = dt.AsEnumerable().Where(myRow => myRow.Field<string>("AppID") == "A0508 - Silverlake Card System");



        }

        private void Form1_Load_1(object sender, EventArgs e)
        {

        }
    }
}