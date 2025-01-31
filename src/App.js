import React, { useState } from 'react';
import { Header } from "./components/Header";
import { Clock } from "./components/Clock";
import { Footer } from "./components/Footer";
import { Button } from "./components/Button";
import { FileUpload } from "./components/FileUpload";
import Config from "./components/Config";
import styled from 'styled-components';

// Custom styling using styled-components!
const AppContainer = styled.div`
  display: flex;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
`;

// Main content area
const MainContent = styled.div`
  margin-left: 320px; /* Adjust for sidebar width */
  width: calc(100% - 320px);
  padding: 20px;
`;

const Section = styled.section`
  width: 100%;
  padding: 20px;
  margin: 20px 0;
  background-color: ${(props) => props.bgColor || "#fff"};
  border-radius: 10px;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
`;

const FileUploadContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 10px;
`;

const ButtonContainer = styled.div`
  margin-top: 20px;
`;

function App() {
  const [fileData, setFileData] = useState(null);
  const [allFilesUploaded, setAllFilesUploaded] = useState(false);
  const [config, setConfig] = useState({
    GPT: true,
    UPDATE_DATABASE: false,
    SEND_DRAFT_WMU: true,
    SEND_DRAFT_JLOH: true,
    WEEKS: 1,
    DELAY: 0,
    UPDATE_DEAL_STATUS: true,
    source_path: "S:\\Data Science\\11. Sourcing and Screening\\5. Weekly Market Update",
    database_path: "C:\\Users\\slu\\AppData\\Local\\Google\\Cloud SDK\\output.csv",
    fivetran_email: "slu@birchhillequity.com",
    email_to: "slu@birchhillequity.com",
    name: "Stephanie",
  });

  const handleFileUpload = (fileData, label) => {
    console.log(fileData);
    setFileData(fileData);

    const originalName = fileData.name;
    const extension = originalName.substring(originalName.lastIndexOf('.'));
    const newName = `${label}${extension}`;

    const fileWithNewName = {
      name: newName,
      content: fileData.content
    };

    console.log('File with new name:', fileWithNewName);

    fetch('http://127.0.0.1:5000/upload', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(fileWithNewName),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log('File uploaded successfully:', data);
      })
      .catch((error) => {
        console.error('Error uploading file:', error);
      });
  };

  const handleAllFilesUploaded = () => {
    setAllFilesUploaded(true);

    fetch('http://127.0.0.1:5000/process-files', {
      method: 'POST',
    })
      .then((response) => response.json())
      .then((data) => {
        console.log('Files processed:', data);
      })
      .catch((error) => {
        console.error('Error processing files:', error);
      });
  };

  const saveConfig = () => {
    console.log("Saving config:", config);
  
    fetch('http://127.0.0.1:5000/save-config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log('Files processed:', data);
      })
      .catch((error) => {
        console.error('Error processing files:', error);
      });
  };

  return (
    <AppContainer>
      <Config config={config} setConfig={setConfig} saveConfig={saveConfig} />

      <MainContent>
        <Header />
        <Clock />
        <Section bgColor="#f0f8ff">
          <h2>Step 1: File Upload</h2>
          <FileUploadContainer>
            <FileUpload label="PE1" onFileUpload={(fileData) => handleFileUpload(fileData, "PE1")} />
            <FileUpload label="PE2" onFileUpload={(fileData) => handleFileUpload(fileData, "PE2")} />
            <FileUpload label="M&A" onFileUpload={(fileData) => handleFileUpload(fileData, "M&A")} />
            <FileUpload label="IPOs" onFileUpload={(fileData) => handleFileUpload(fileData, "IPOs")} />
            <FileUpload label="MGMT" onFileUpload={(fileData) => handleFileUpload(fileData, "MGMT")} />
          </FileUploadContainer>
          <ButtonContainer>
            <Button onClick={handleAllFilesUploaded} label="I’ve uploaded all files" hasUploaded={allFilesUploaded} />
          </ButtonContainer>
        </Section>

        <Section>
          <h2>Step 2: Display Table</h2>
        </Section>
        <Section>
          <h2>Step 3: Additional Content</h2>
        </Section>
        <Footer />
      </MainContent>
    </AppContainer>
  );
}

export default App;
