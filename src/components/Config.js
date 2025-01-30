import React, { useState } from 'react';
import styled from 'styled-components';
import { FiSave, FiChevronLeft, FiChevronRight } from 'react-icons/fi';

// Sidebar Container - Floating Flat Panel
const SidebarContainer = styled.div`
  position: fixed;
  left: ${(props) => (props.collapsed ? '-350px' : '20px')}; /* Moves completely out when collapsed */
  top: 20px;
  width: 300px;
  background: white;
  border-radius: 12px;
  box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);
  padding: 20px 25px;
  transition: all 0.3s ease-in-out;
  z-index: 1000;
`;

const BackgroundOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, ${(props) => (props.collapsed ? '0' : '0.4')}); /* No dark grey when collapsed */
  transition: background 0.3s ease-in-out;
  pointer-events: ${(props) => (props.collapsed ? 'none' : 'auto')};
`;

const ToggleButton = styled.button`
  position: absolute;
  left: 100%;
  top: 15px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  
  &:hover {
    background: #005bbf;
  }
`;

const ConfigHeader = styled.h2`
  font-size: 1.4rem;
  font-weight: 600;
  margin-bottom: 15px;
  color: #333;
`;

const ConfigOption = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f9f9f9;
  border-radius: 8px;
  padding: 12px 15px;
  margin-bottom: 10px;
  transition: all 0.3s ease;

  &:hover {
    background: #f0f4ff;
  }
`;

const Label = styled.label`
  font-size: 1rem;
  font-weight: 500;
  color: #444;
`;

const Checkbox = styled.input`
  width: 20px;
  height: 20px;
  cursor: pointer;
  accent-color: #007bff;
`;

const Input = styled.input`
  width: 100px;
  padding: 6px 10px;
  border: 1px solid #ccc;
  border-radius: 6px;
  text-align: center;
  font-size: 1rem;
  color: #333;
  background: #fff;
  transition: all 0.2s ease;

  &:focus {
    border-color: #007bff;
    outline: none;
  }
`;

const SaveButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 15px;
  font-size: 1rem;
  font-weight: 500;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: #005bbf;
  }
`;

function Config() {
  const [collapsed, setCollapsed] = useState(false);
  const [config, setConfig] = useState({
    GPT: false,
    UPDATE_DATABASE: false,
    SEND_DRAFT_WMU: false,
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

  const handleChange = (key, value) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  };

  const saveConfig = () => {
    console.log("Saving config:", config);

    fetch('http://127.0.0.1:5000/save-config', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log('Config saved:', data);
      })
      .catch((error) => {
        console.error('Error saving config:', error);
      });
  };

  return (
    <>
      <BackgroundOverlay collapsed={collapsed} onClick={() => setCollapsed(true)} />
      <SidebarContainer collapsed={collapsed}>
        <ToggleButton onClick={() => setCollapsed(!collapsed)}>
          {collapsed ? <FiChevronRight size={18} /> : <FiChevronLeft size={18} />}
        </ToggleButton>

        {!collapsed && (
          <>
            <ConfigHeader>⚙️ Configuration</ConfigHeader>
            {Object.keys(config).map((key) => (
              <ConfigOption key={key}>
                <Label>{key.replace(/_/g, ' ')}</Label>
                {typeof config[key] === 'boolean' ? (
                  <Checkbox
                    type="checkbox"
                    checked={config[key]}
                    onChange={(e) => handleChange(key, e.target.checked)}
                  />
                ) : (
                  <Input
                    type="text"
                    value={config[key]}
                    onChange={(e) => handleChange(key, e.target.value)}
                  />
                )}
              </ConfigOption>
            ))}
            <SaveButton onClick={saveConfig}>
              <FiSave size={18} /> Save Config
            </SaveButton>
          </>
        )}
      </SidebarContainer>
    </>
  );
}

export default Config;
