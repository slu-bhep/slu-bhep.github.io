import React, { useState } from 'react';

import { Header } from "./components/Header";
import { Clock } from "./components/Clock";
import { Footer } from "./components/Footer";
import styled from 'styled-components';

import { FileUpload } from "./components/FileUpload";
import ExcelTable from "./components/ExcelTable"; // Import ExcelTable component

// custom styling using styled-components!
const AppContainer = styled.div`
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
  max-width: 1200px;
  padding: 20px;
`;

const Section = styled.section`
  width: 100%;
  padding: 20px;
  margin: 20px 0;
  background-color: ${(props) => props.bgColor || "#fff"};
  border-radius: 10px;
  box-shadow: ${(props) => props.shadow || "none"};
`;

const FileUploadContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 10px;
`;

function App() {
  const [fileData, setFileData] = useState(null); // State to hold the uploaded file data

  const handleFileUpload = (fileData) => {
    console.log(fileData); // Log the uploaded file data
    setFileData(fileData); // Set the uploaded file data to state
  };

  return (
    <AppContainer>
      <Header />
      <Clock />
      <Section bgColor="#f0f8ff" shadow="0px 4px 8px rgba(0, 0, 0, 0.1)">
        <h2>Step 1: File Upload</h2>
        <FileUploadContainer>
          <FileUpload label="PE1" onFileUpload={handleFileUpload} />
          <FileUpload label="PE2" onFileUpload={handleFileUpload} />
          <FileUpload label="M&A" onFileUpload={handleFileUpload} />
          <FileUpload label="IPOs" onFileUpload={handleFileUpload} />
          <FileUpload label="MGMT" onFileUpload={handleFileUpload} />
        </FileUploadContainer>
      </Section>
      <Section bgColor="#fff" shadow="0px 4px 8px rgba(0, 0, 0, 0.1)">
        <h2>Step 2: Display Table</h2>
        {/* Only show the table if file data exists */}
        {fileData && fileData.content && (
          <ExcelTable fileData={fileData} />
        )}
      </Section>
      <Section bgColor="#fff" shadow="0px 4px 8px rgba(0, 0, 0, 0.1)">
        <h2>Step 3: Additional Content</h2>
      </Section>
      <Footer />
    </AppContainer>
  );
}

export default App;
