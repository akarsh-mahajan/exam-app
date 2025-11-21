import React from 'react';
import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header style={{ padding: '1rem', backgroundColor: '#f0f0f0' }}>
      <Link to="/">
        <button>Home</button>
      </Link>
    </header>
  );
};

export default Header;
