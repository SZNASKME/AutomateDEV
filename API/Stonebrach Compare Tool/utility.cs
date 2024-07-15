using System;
using System.Collections.Generic;
using System.Data;
using System.IO;
using System.IO.Packaging;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using OfficeOpenXml;
namespace Stonebrach_Compare_Tool
{
    internal class utility
    {
        public ExcelWorksheet GetWorksheetDetail()
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            DataTable table = new DataTable();
            var fi = new FileInfo(@"D:\DotNet Project\Stonebrach Compare Tool\TTB Data.xlsx");
            ExcelPackage package = new ExcelPackage(fi);
            var worksheet = package.Workbook.Worksheets["Sheet"];

            
            /* int noOfCol = worksheet.Dimension.End.Column;
             int noOfRow = worksheet.Dimension.End.Row;
             int rowIndex = 1;
             for (int c = 1; c <= noOfCol; c++)
             {
                 table.Columns.Add(worksheet.Cells[rowIndex, c].Text);
             }*/
            
          

                return worksheet;

        }

        public DataTable ExceltoDatatable()
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            DataTable table = new DataTable();
            var fi = new FileInfo(@"D:\DotNet Project\Stonebrach Compare Tool\TTB Data.xlsx");
            ExcelPackage package = new ExcelPackage(fi);
            var worksheet = package.Workbook.Worksheets["Sheet"];


            int noOfCol = worksheet.Dimension.End.Column;
            int noOfRow = worksheet.Dimension.End.Row;
            int rowIndex = 1;
            for (int c = 1; c <= noOfCol; c++)
            {
                table.Columns.Add(worksheet.Cells[rowIndex, c].Text);
            }
            rowIndex = 2;
            for (int r = rowIndex; r <= noOfRow; r++)
            {
                DataRow dr = table.NewRow();
                for (int c = 1; c <= noOfCol; c++)
                {
                    dr[c - 1] = worksheet.Cells[r, c].Value;
                }
                table.Rows.Add(dr);
            }


            return table;

        }


    }
}
