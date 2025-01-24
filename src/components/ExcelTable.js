import React, { useState } from "react";
import * as XLSX from "xlsx"; // Import the xlsx library

const ExcelTable = ({ fileData }) => {
  const [tableData, setTableData] = useState([]);

  // Function to process the uploaded Excel file
  const processFile = (fileData) => {
    const binaryData = atob(fileData.content.split(",")[1]); // Decode the base64 content from the uploaded file
    const buffer = new ArrayBuffer(binaryData.length);
    const view = new Uint8Array(buffer);

    for (let i = 0; i < binaryData.length; i++) {
      view[i] = binaryData.charCodeAt(i);
    }

    // Read the file using xlsx library
    const workbook = XLSX.read(buffer, { type: "array" });
    const sheet = workbook.Sheets[workbook.SheetNames[0]]; // Get the first sheet

    // Convert sheet data to JSON
    const jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 }); // 'header: 1' keeps the raw rows in an array format

    const filteredData = jsonData.slice(6, jsonData.length ); // Skip the first 6 rows and no footer rows

    // Extract the first 3 columns
    const cleanedData = filteredData.map(row => row.slice(0, 3));

    // Set the table data state
    setTableData(cleanedData);
  };

  // When fileData is updated, process the new file
  React.useEffect(() => {
    if (fileData?.content) {
      processFile(fileData);
    }
  }, [fileData]);

  return (
    <div>
      <h3>Uploaded Data (First 3 Columns)</h3>
      <table border="1" style={{ width: "100%", textAlign: "left", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>Column 1</th>
            <th>Column 2</th>
            <th>Column 3</th>
          </tr>
        </thead>
        <tbody>
          {tableData.map((row, index) => (
            <tr key={index}>
              <td>{row[0]}</td>
              <td>{row[1]}</td>
              <td>{row[2]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ExcelTable;
