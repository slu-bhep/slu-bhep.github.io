import React from 'react';
import styled from 'styled-components';

// Custom Button styling for a more subtle design
const StyledButton = styled.button`
  background-color: #f0f0f0; /* Light background color */
  color: #333; /* Dark text color */
  border: 1px solid #ddd; /* Subtle border */
  padding: 8px 16px;
  font-size: 16px;
  border-radius: 4px; /* Slight rounding for softer corners */
  cursor: pointer;
  transition: background-color 0.3s ease, border-color 0.3s ease;

  &:hover {
    background-color: #e0e0e0; /* Slightly darker on hover */
    border-color: #bbb; /* Darker border on hover */
  }

  &:active {
    background-color: #d0d0d0; /* Even darker on click */
  }
`;

const Button = ({ onClick, label, hasUploaded }) => (
  <StyledButton onClick={onClick} disabled={hasUploaded}>
    {hasUploaded ? "You've uploaded all files!" : label}
  </StyledButton>
);

export { Button };
