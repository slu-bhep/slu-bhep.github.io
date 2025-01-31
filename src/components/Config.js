import React, { useState } from 'react';
import styled from 'styled-components';
import { FiSave, FiChevronLeft, FiChevronRight } from 'react-icons/fi';

// Sidebar Container - Floating Flat Panel
const SidebarContainer = styled.div`
  position: fixed;
  left: ${(props) => (props.collapsed ? '-350px' : '20px')};
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
  background: rgba(0, 0, 0, ${(props) => (props.collapsed ? '0' : '0.05')});
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
  position: relative;

  &:hover {
    background: #f0f4ff;
  }
`;

const Label = styled.label`
  font-size: 1rem;
  font-weight: 500;
  color: #444;
  display: flex;
  align-items: center;
`;

const Tooltip = styled.div`
  position: absolute;
  background-color: #333;
  color: white;
  padding: 8px;
  border-radius: 5px;
  font-size: 0.9rem;
  z-index: 9999;
  top: 50%;
  left: 100%;
  transform: translateX(10px) translateY(-50%);
  white-space: nowrap;
  visibility: hidden;
  opacity: 0;
  transition: opacity 0.2s;

  ${ConfigOption}:hover & {
    visibility: visible;
    opacity: 1;
  }
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

const LABELS = {
  GPT: "Use GPT",
  UPDATE_DATABASE: "Update Database",
  SEND_DRAFT_WMU: "Send WMU Draft",
  SEND_DRAFT_JLOH: "Send JLoh Draft",
  WEEKS: "Weeks",
  DELAY: "Delay (Days from Thursday)",
  UPDATE_DEAL_STATUS: "Update Deal Status",
  source_path: "Source Files Path",
  database_path: "Database Path",
  fivetran_email: "Fivetran Email",
  email_to: "Recipient Email",
  name: "Name",
};

const TOOLTIP_TEXT = {
  GPT: "Use GPT to write and format the WMU.",
  UPDATE_DATABASE: "Update BigQuery tables with new deal data.",
  SEND_DRAFT_WMU: "Send yourself a draft of the WMU email.",
  SEND_DRAFT_JLOH: "Send yourself a draft of the WMU Check email to JLoh.",
  WEEKS: "Number of weeks of deals covered in the WMU.",
  DELAY: "Number of days we are from Thursday.",
  UPDATE_DEAL_STATUS: "Update 'In DealCloud', 'In Market', and 'Reviewed by BH' fields.",
  source_path: "Path to the source files for deal data.",
  database_path: "Path to BigQuery tables.",
  fivetran_email: "Fivetran email used for syncing data to BigQuery.",
  email_to: "Email address to send the email drafts.",
  name: "Name to use for the email salutations.",
};

function Config({ config, setConfig, saveConfig }) {
  const [collapsed, setCollapsed] = useState(false);

  const handleChange = (key, value) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
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
                <Label>
                  {LABELS[key] || key.replace(/_/g, ' ')}
                  <Tooltip>{TOOLTIP_TEXT[key] || "No description available."}</Tooltip>
                </Label>
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
