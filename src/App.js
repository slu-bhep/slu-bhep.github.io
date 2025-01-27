import React, { useState } from 'react';

import { Header } from "./components/Header";
import { Clock } from "./components/Clock";
import { Footer } from "./components/Footer";
import styled from 'styled-components';

import { FileUpload } from "./components/FileUpload";

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

  const handleFileUpload = (fileData, label) => {
    console.log(fileData); // Log the uploaded file data
    setFileData(fileData); // Set the uploaded file data to state

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
      })
  };

  return (
    <AppContainer>
      <Header />
      <Clock />
      <Section bgColor="#f0f8ff" shadow="0px 4px 8px rgba(0, 0, 0, 0.1)">
        <h2>Step 1: File Upload</h2>
        <FileUploadContainer>
          <FileUpload label="PE1" onFileUpload={(fileData) => handleFileUpload(fileData, "PE1")} />
          <FileUpload label="PE2" onFileUpload={(fileData) => handleFileUpload(fileData, "PE2")} />
          <FileUpload label="M&A" onFileUpload={(fileData) => handleFileUpload(fileData, "M&A")} />
          <FileUpload label="IPOs" onFileUpload={(fileData) => handleFileUpload(fileData, "IPOs")} />
          <FileUpload label="MGMT" onFileUpload={(fileData) => handleFileUpload(fileData, "MGMT")} />
        </FileUploadContainer>
      </Section>
      <Section bgColor="#fff" shadow="0px 4px 8px rgba(0, 0, 0, 0.1)">
        <h2>Step 2: Display Table</h2>
      </Section>
      <Section bgColor="#fff" shadow="0px 4px 8px rgba(0, 0, 0, 0.1)">
        <h2>Step 3: Additional Content</h2>
      </Section>
      <Footer />
    </AppContainer>
  );
}

export default App;
