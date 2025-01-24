import React, { useRef, useState } from "react";
import styled from "styled-components";

// Styled-components for basic styling
const UploadContainer = styled.div`
  padding: 20px;
  border: 2px dashed #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
  text-align: center;
  width: 150px;
  transition: border-color 0.3s ease;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;  // Center the content vertically

  &:hover {
    border-color: #4da6ff;
  }

  &:active {
    background-color: #eef9ff;
  }
`;

const FileInput = styled.input`
  display: none;
`;

const ChooseFileButton = styled.label`
  display: inline-block;
  background-color: #4da6ff;
  color: white;
  padding: 12px 20px;
  font-size: 16px;
  cursor: pointer;
  border-radius: 8px;
  transition: background-color 0.3s ease, transform 0.3s ease;

  &:hover {
    background-color: #3399ff;
    transform: scale(1.05);
  }

  &:active {
    background-color: #2980b9;
  }
`;

const FileNameText = styled.p`
  font-size: 14px;
  color: #555;
  margin-top: 10px;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
`;

const LabelText = styled.h3`
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
`;

const ErrorText = styled.p`
  font-size: 12px;
  color: #e74c3c;
  margin-top: 10px;
`;

const ProgressBarContainer = styled.div`
  width: 100%;
  height: 6px;
  background-color: #ddd;
  margin-top: 10px;
  border-radius: 5px;
`;

const ProgressBar = styled.div`
  height: 100%;
  background-color: ${(props) => (props.progress === 100 ? '#2ecc71' : '#4da6ff')}; /* Green when done */
  width: ${(props) => props.progress}%;
  border-radius: 5px;
  transition: width 0.3s ease-in-out;
`;

const RemoveFileButton = styled.button`
  background-color: transparent;
  border: none;
  color: #e74c3c;
  font-size: 18px;
  cursor: pointer;
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 0;
  transition: color 0.3s ease;

  &:hover {
    color: #c0392b;
  }
`;

export const FileUpload = ({ label, onFileUpload }) => {
  const fileInputRef = useRef();
  const [fileName, setFileName] = useState("");
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);

  const validFileTypes = [
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", // .xlsx
    "application/vnd.ms-excel", // .xls
    "text/csv" // .csv
  ];

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      const file = files[0];
      if (!validFileTypes.includes(file.type)) {
        setError("Invalid file type. Please upload a .csv or .xlsx or .xls file.");
        return;
      }
      setError(null);

      setFileName(file.name);
      uploadFile(file);
    }
  };

  const uploadFile = (file) => {
    const reader = new FileReader();
    reader.onloadstart = () => {
      setUploadProgress(0);
    };

    reader.onprogress = (event) => {
      if (event.lengthComputable) {
        const progress = Math.round((event.loaded / event.total) * 100);
        setUploadProgress(progress);
      }
    };

    reader.onload = () => {
      onFileUpload({
        name: file.name,
        content: reader.result,
      });
      setUploadProgress(100);
    };

    reader.onerror = () => {
      setError("There was an error uploading the file.");
    };

    reader.readAsText(file);
  };

  const removeFile = () => {
    setFileName(""); // Clear file name
    setUploadProgress(0); // Reset progress bar
    setError(null); // Reset error message
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      const file = files[0];
      handleFileChange({ target: { files: [file] } });
    }
  };

  return (
    <UploadContainer
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      style={{ position: "relative" }} // Add position relative for the remove button to work
    >
      <LabelText>{label}</LabelText>
      <FileInput
        ref={fileInputRef}
        type="file"
        onChange={handleFileChange}
        id={`file-upload-${label}`}
      />
      <ChooseFileButton htmlFor={`file-upload-${label}`}>
        {fileName ? "Uploaded!" : "Choose Files"}
      </ChooseFileButton>
      {fileName && (
        <RemoveFileButton onClick={removeFile}>×</RemoveFileButton>
      )}
      {error && <ErrorText>{error}</ErrorText>}
      {uploadProgress > 0 && (
        <>
          <ProgressBarContainer>
            <ProgressBar progress={uploadProgress} />
          </ProgressBarContainer>
        </>
      )}
      {fileName && <FileNameText title={fileName}>{fileName}</FileNameText>}
    </UploadContainer>
  );
};
